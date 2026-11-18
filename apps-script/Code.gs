/**
 * Tax Receipt Sorter: sheet bridge.
 *
 * Claude can read and create files in Google Drive, but it cannot edit a
 * Google Sheet. This script is the bridge. On a timer it:
 *   1. reads the "rows-*.txt" files Claude left in the mailbox folder and
 *      applies them to the Expenses tab, then
 *   2. writes "sheet-snapshot.txt" there, so Claude can see the whole sheet.
 *
 * The mailbox is a folder called "_claude" inside your receipts folder
 * (My situation, cell B5). The script runs as you, inside your own Google
 * account. It never deletes anything and never edits a row whose Status is
 * Approved, Rejected or blank.
 *
 * Set up: Extensions > Apps Script, paste this file, save, then run "setup".
 * If cell B5 is empty, setup creates a folder called "Receipts inbox" next to
 * the sheet and fills in B5 for you.
 */

const TABS = { expenses: 'Expenses', categories: 'Categories', situation: 'My situation' };
const MAILBOX = '_claude';
const DONE = 'done';
const SNAPSHOT = 'sheet-snapshot.txt';
const CLAUDE_STATUSES = ['Suggested', 'Needs answer'];
const COL = {
  date: 1, item: 2, vendor: 3, category: 4, purpose: 5, qty: 6, unit: 7, total: 8,
  use: 9, deductible: 10, receipt: 11, notes: 12, status: 13, question: 14, answer: 15, source: 16,
};

/**
 * Run once. Makes a receipts folder if My situation B5 is empty, starts the
 * hourly timer and does a first sync.
 */
function setup() {
  ensureReceiptsFolder_(SpreadsheetApp.getActive());
  ScriptApp.getProjectTriggers()
    .filter((t) => t.getHandlerFunction() === 'sync')
    .forEach((t) => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('sync').timeBased().everyHours(1).create();
  sync();
}

/** Adds the Tax assistant menu to the sheet. Runs by itself when the sheet opens. */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Tax assistant')
    .addItem('Set up (run once)', 'setup')
    .addItem('Sync now', 'sync')
    .addToUi();
}

/** Apply Claude's pending rows, then refresh the snapshot. */
function sync() {
  const lock = LockService.getDocumentLock();
  if (!lock.tryLock(30000)) return;
  try {
    const ss = SpreadsheetApp.getActive();
    const box = mailbox_(ss);
    importOutbox_(ss, box);
    SpreadsheetApp.flush();
    writeSnapshot_(ss, box);
  } finally {
    lock.releaseLock();
  }
}

// ------------------------------------------------------------------ mailbox

function mailbox_(ss) {
  const cell = ss.getSheetByName(TABS.situation).getRange('B5');
  let link = String(cell.getValue() || '');
  const rich = cell.getRichTextValue();
  if (rich && rich.getLinkUrl()) link = rich.getLinkUrl();
  const match = link.match(/folders\/([\w-]+)/) || link.match(/[?&]id=([\w-]+)/);
  if (!match) throw new Error('My situation B5 must hold the link to your receipts folder.');
  return childFolder_(DriveApp.getFolderById(match[1]), MAILBOX);
}

/** If B5 is empty, create "Receipts inbox" next to the sheet and put its link in B5. */
function ensureReceiptsFolder_(ss) {
  const cell = ss.getSheetByName(TABS.situation).getRange('B5');
  if (String(cell.getValue() || '').trim()) return;
  const parents = DriveApp.getFileById(ss.getId()).getParents();
  const home = parents.hasNext() ? parents.next() : DriveApp.getRootFolder();
  cell.setValue(childFolder_(home, 'Receipts inbox').getUrl());
  SpreadsheetApp.flush();
}

function childFolder_(parent, name) {
  const found = parent.getFoldersByName(name);
  return found.hasNext() ? found.next() : parent.createFolder(name);
}

// ------------------------------------------------------------------- import

function importOutbox_(ss, box) {
  const files = [];
  const it = box.getFiles();
  while (it.hasNext()) {
    const f = it.next();
    if (/^rows-/.test(f.getName())) files.push(f);
  }
  if (!files.length) return;
  files.sort((a, b) => (a.getName() < b.getName() ? -1 : 1));

  const sh = ss.getSheetByName(TABS.expenses);
  if (String(sh.getRange(1, COL.status).getValue()).trim() !== 'Status') {
    throw new Error('Expenses column M must be headed "Status".');
  }
  const cats = categoryNames_(ss);
  const done = childFolder_(box, DONE);
  const log = [];

  files.forEach((file) => {
    let ops;
    try {
      ops = JSON.parse(file.getBlob().getDataAsString('UTF-8')).rows;
      if (!Array.isArray(ops)) throw new Error('no "rows" list');
    } catch (e) {
      file.setName('error-' + file.getName());
      log.push(file.getName() + ': could not be read (' + e.message + ')');
      return;
    }
    ops.forEach((op) => {
      let result;
      try {
        result = op.action === 'update' ? updateRow_(sh, cats, op) : addRow_(sh, cats, op);
      } catch (e) {
        result = 'failed: ' + e.message;
      }
      log.push(file.getName() + ' ' + (op.sourceId || '(no sourceId)') + ': ' + result);
    });
    file.moveTo(done);
  });

  const stamp = Utilities.formatDate(new Date(), 'UTC', "yyyy-MM-dd'T'HH:mm'Z'");
  PropertiesService.getDocumentProperties().setProperty(
    'lastImport',
    JSON.stringify({ at: stamp, lines: log.slice(-60) })
  );
}

function categoryNames_(ss) {
  const sh = ss.getSheetByName(TABS.categories);
  const values = sh.getRange(2, 1, Math.max(sh.getLastRow() - 1, 1), 1).getValues();
  const names = [];
  for (let i = 0; i < values.length; i++) {
    const name = String(values[i][0]).trim();
    if (!name || /^total/i.test(name)) break;
    names.push(name);
  }
  return names;
}

/** Row numbers by Source ID, the TOTAL row (0 if none) and the last data row. */
function layout_(sh) {
  const last = Math.max(sh.getLastRow(), 1);
  const values = sh.getRange(1, 1, last, COL.source).getValues();
  let total = 0;
  for (let i = 1; i < values.length; i++) {
    if (/^total/i.test(String(values[i][0]).trim())) { total = i + 1; break; }
  }
  const end = total ? total - 1 : last;
  const bySource = {};
  let lastData = 1;
  for (let i = 1; i < end; i++) {
    const row = values[i];
    const source = String(row[COL.source - 1]).trim();
    if (source) bySource[source] = i + 1;
    const used = [COL.date, COL.item, COL.vendor, COL.unit, COL.source].some((c) => row[c - 1] !== '');
    if (used) lastData = i + 1;
  }
  return { total: total, lastData: lastData, bySource: bySource, values: values };
}

function addRow_(sh, cats, op) {
  if (!op.sourceId) return 'skipped: no sourceId';
  const lay = layout_(sh);
  if (lay.bySource[op.sourceId]) return 'skipped: already in row ' + lay.bySource[op.sourceId];

  let r = lay.lastData + 1;
  if (lay.total && r >= lay.total) {
    sh.insertRowBefore(lay.total);
    r = lay.total;
  }

  let status = CLAUDE_STATUSES.indexOf(op.status) >= 0 ? op.status : 'Needs answer';
  let question = op.question || '';
  let category = op.category || '';
  if (category && cats.indexOf(category) < 0) {
    question = 'Category "' + category + '" is not in the Categories tab. ' + question;
    category = '';
    status = 'Needs answer';
  }

  setIf_(sh, r, COL.date, parseDate_(op.date));
  setIf_(sh, r, COL.item, op.item);
  setIf_(sh, r, COL.vendor, op.vendor);
  setIf_(sh, r, COL.category, category);
  setIf_(sh, r, COL.purpose, op.purpose);
  sh.getRange(r, COL.qty).setValue(typeof op.qty === 'number' ? op.qty : 1);
  if (typeof op.unitPrice === 'number') sh.getRange(r, COL.unit).setValue(op.unitPrice);
  setFormulas_(sh, r, lay.lastData);
  setUse_(sh, r, op.businessUse);
  if (op.receiptUrl) {
    sh.getRange(r, COL.receipt).setRichTextValue(
      SpreadsheetApp.newRichTextValue().setText(op.receiptName || 'receipt').setLinkUrl(op.receiptUrl).build()
    );
  }
  setIf_(sh, r, COL.notes, op.notes);
  sh.getRange(r, COL.status).setValue(status);
  setIf_(sh, r, COL.question, question);
  sh.getRange(r, COL.source).setValue(op.sourceId);
  return 'added to row ' + r + ' as ' + status;
}

function updateRow_(sh, cats, op) {
  const lay = layout_(sh);
  const r = lay.bySource[op.sourceId];
  if (!r) return 'skipped: no row with this Source ID';
  const current = String(lay.values[r - 1][COL.status - 1]).trim();
  if (CLAUDE_STATUSES.indexOf(current) < 0) {
    return 'skipped: row ' + r + ' is "' + (current || 'blank') + '", only you can change it';
  }
  if (op.category !== undefined) {
    if (cats.indexOf(op.category) < 0) return 'skipped: category "' + op.category + '" is not in the Categories tab';
    sh.getRange(r, COL.category).setValue(op.category);
  }
  if (op.date !== undefined) {
    const d = parseDate_(op.date);
    if (!d) return 'skipped: date "' + op.date + '" is not YYYY-MM-DD';
    sh.getRange(r, COL.date).setValue(d);
  }
  if (op.item !== undefined) sh.getRange(r, COL.item).setValue(op.item);
  if (op.vendor !== undefined) sh.getRange(r, COL.vendor).setValue(op.vendor);
  if (typeof op.qty === 'number') sh.getRange(r, COL.qty).setValue(op.qty);
  if (op.purpose !== undefined) sh.getRange(r, COL.purpose).setValue(op.purpose);
  if (typeof op.unitPrice === 'number') sh.getRange(r, COL.unit).setValue(op.unitPrice);
  if (op.businessUse !== undefined) setUse_(sh, r, op.businessUse);
  if (op.question !== undefined) sh.getRange(r, COL.question).setValue(op.question);
  if (op.notesAppend) {
    const cell = sh.getRange(r, COL.notes);
    const old = String(cell.getValue() || '');
    cell.setValue(old ? old + '; ' + op.notesAppend : op.notesAppend);
  }
  if (CLAUDE_STATUSES.indexOf(op.status) >= 0) sh.getRange(r, COL.status).setValue(op.status);
  return 'updated row ' + r;
}

function setIf_(sh, r, c, value) {
  if (value !== undefined && value !== null && value !== '') sh.getRange(r, c).setValue(value);
}

function parseDate_(text) {
  const m = String(text || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
  return m ? new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])) : null;
}

/** Total paid and Deductible amount: copy your own formulas from the row above when it has them. */
function setFormulas_(sh, r, above) {
  [COL.total, COL.deductible].forEach((c) => {
    const source = sh.getRange(above, c);
    if (above > 1 && source.getFormula()) {
      source.copyTo(sh.getRange(r, c), SpreadsheetApp.CopyPasteType.PASTE_FORMULA, false);
    } else if (c === COL.total) {
      sh.getRange(r, c).setFormula('=IF(G' + r + '="";"";IF(F' + r + '="";1;F' + r + ')*G' + r + ')');
    } else {
      sh.getRange(r, c).setFormula(
        '=IF(H' + r + '="";"";H' + r + '*IF(I' + r + '="";1;I' + r + ')*IF(D' + r + '="Meals (50%)";1/2;1))'
      );
    }
  });
}

/**
 * Business use %: a share from 0 to 1, or {num, den}: two amounts printed on
 * the receipt. The division is left to the sheet, written in whole cents so
 * it reads the same in every locale.
 */
function setUse_(sh, r, use) {
  const cell = sh.getRange(r, COL.use);
  if (use === null || use === '') {
    cell.clearContent();
  } else if (typeof use === 'number' && use >= 0 && use <= 1) {
    cell.setValue(use).setNumberFormat('0.00%');
  } else if (use && typeof use.num === 'number' && typeof use.den === 'number' && use.den > 0) {
    cell.setFormula('=' + Math.round(use.num * 100) + '/' + Math.round(use.den * 100)).setNumberFormat('0.00%');
  }
}

// ----------------------------------------------------------------- snapshot

function writeSnapshot_(ss, box) {
  const tz = ss.getSpreadsheetTimeZone();
  const text = (v) => {
    if (v instanceof Date) return Utilities.formatDate(v, tz, 'yyyy-MM-dd');
    return String(v === null || v === undefined ? '' : v).replace(/\s+/g, ' ').trim();
  };
  const out = [];
  out.push('TAX SHEET SNAPSHOT (format 1)');
  out.push('written: ' + Utilities.formatDate(new Date(), 'UTC', "yyyy-MM-dd'T'HH:mm'Z'"));
  out.push('sheet: ' + ss.getName());
  out.push('fields are separated by " :: "; numbers use a decimal point; business use 0.5 means 50%');

  const sit = ss.getSheetByName(TABS.situation);
  const sitValues = sit.getRange(1, 1, Math.max(sit.getLastRow(), 24), 5).getValues();
  out.push('', '== My situation: cell :: setting :: answer');
  for (let r = 4; r <= 22; r++) {
    if (text(sitValues[r - 1][0])) out.push('B' + r + ' :: ' + text(sitValues[r - 1][0]) + ' :: ' + text(sitValues[r - 1][1]));
  }
  out.push('', '== Vendor rules: contains :: category :: business use :: note :: file into folder');
  for (let r = 25; r <= sitValues.length; r++) {
    const row = sitValues[r - 1];
    if (text(row[0])) out.push(row.map(text).join(' :: '));
  }

  const cat = ss.getSheetByName(TABS.categories);
  const catValues = cat.getRange(2, 1, Math.max(cat.getLastRow() - 1, 1), 6).getValues();
  out.push('', '== Categories: name :: form line :: receipt folder');
  for (let i = 0; i < catValues.length; i++) {
    const name = text(catValues[i][0]);
    if (!name || /^total/i.test(name)) break;
    out.push(name + ' :: ' + text(catValues[i][1]) + ' :: ' + text(catValues[i][5]));
  }

  const sh = ss.getSheetByName(TABS.expenses);
  const lay = layout_(sh);
  const waiting = [];
  out.push('', '== Expenses: row :: date :: vendor :: item :: category :: unit price :: business use :: status :: source id');
  for (let r = 2; r <= lay.lastData; r++) {
    const row = lay.values[r - 1];
    const get = (c) => text(row[c - 1]);
    out.push(
      [r, get(COL.date), get(COL.vendor), get(COL.item), get(COL.category), get(COL.unit), get(COL.use),
        get(COL.status) || '(blank: typed by hand)', get(COL.source)].join(' :: ')
    );
    if (get(COL.status) === 'Needs answer') {
      waiting.push(
        'row ' + r + ' :: source id: ' + get(COL.source) + ' :: question: ' + get(COL.question) +
        ' :: your answer: ' + (get(COL.answer) || '(none yet)') + ' :: purpose: ' + get(COL.purpose) +
        ' :: notes: ' + get(COL.notes)
      );
    }
  }
  out.push('first empty row: ' + (lay.lastData + 1) + (lay.total ? ' (TOTAL row is ' + lay.total + ')' : ''));

  out.push('', '== Rows with Status "Needs answer"');
  out.push(waiting.length ? waiting.join('\n') : '(none)');

  out.push('', '== Last import');
  const saved = PropertiesService.getDocumentProperties().getProperty('lastImport');
  if (saved) {
    const last = JSON.parse(saved);
    out.push('at: ' + last.at);
    last.lines.forEach((line) => out.push(line));
  } else {
    out.push('(nothing imported yet)');
  }

  const body = out.join('\n') + '\n';
  const existing = box.getFilesByName(SNAPSHOT);
  if (existing.hasNext()) existing.next().setContent(body);
  else box.createFile(SNAPSHOT, body, MimeType.PLAIN_TEXT);
}
