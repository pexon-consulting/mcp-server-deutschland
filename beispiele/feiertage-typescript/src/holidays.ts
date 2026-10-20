// Gesetzliche Feiertage in Deutschland, ohne externe API berechnet.
// Feiertage, die nur in einzelnen Gemeinden gelten, sind nicht enthalten.

export const STATES = {
  BW: "Baden-Württemberg",
  BY: "Bayern",
  BE: "Berlin",
  BB: "Brandenburg",
  HB: "Bremen",
  HH: "Hamburg",
  HE: "Hessen",
  MV: "Mecklenburg-Vorpommern",
  NI: "Niedersachsen",
  NW: "Nordrhein-Westfalen",
  RP: "Rheinland-Pfalz",
  SL: "Saarland",
  SN: "Sachsen",
  ST: "Sachsen-Anhalt",
  SH: "Schleswig-Holstein",
  TH: "Thüringen",
} as const;

export type StateCode = keyof typeof STATES;
export const STATE_CODES = Object.keys(STATES) as StateCode[];

export const MIN_YEAR = 1995;
export const MAX_YEAR = 2100;

export interface Holiday {
  date: string; // JJJJ-MM-TT
  name: string;
  nationwide: boolean;
}

// Alle Datumswerte in UTC, damit Sommerzeit keine Tage verschiebt.
const utc = (y: number, m: number, d: number) => new Date(Date.UTC(y, m - 1, d));
const addDays = (d: Date, n: number) => new Date(d.getTime() + n * 86_400_000);
export const iso = (d: Date) => d.toISOString().slice(0, 10);

export function easterSunday(year: number): Date {
  const a = year % 19;
  const b = Math.floor(year / 100);
  const c = year % 100;
  const d = Math.floor(b / 4);
  const e = b % 4;
  const f = Math.floor((b + 8) / 25);
  const g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4);
  const k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7;
  const m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31);
  const day = ((h + l - 7 * m + 114) % 31) + 1;
  return utc(year, month, day);
}

function repentanceDay(year: number): Date {
  // Mittwoch vor dem 23. November
  const nov22 = utc(year, 11, 22);
  const back = (nov22.getUTCDay() - 3 + 7) % 7;
  return addDays(nov22, -back);
}

export function checkState(state: string): StateCode {
  const code = state.trim().toUpperCase();
  if (!(code in STATES)) {
    throw new Error(`Unbekanntes Bundesland '${state}'. Erlaubt sind: ${STATE_CODES.join(", ")}.`);
  }
  return code as StateCode;
}

export function holidays(year: number, state: string): Holiday[] {
  if (!Number.isInteger(year) || year < MIN_YEAR || year > MAX_YEAR) {
    throw new Error(`Jahr ${year} wird nicht unterstützt. Erlaubt ist ${MIN_YEAR} bis ${MAX_YEAR}.`);
  }
  const st = checkState(state);
  const easter = easterSunday(year);
  const list: Holiday[] = [];
  const nat = (d: Date, name: string) => list.push({ date: iso(d), name, nationwide: true });
  const reg = (d: Date, name: string) => list.push({ date: iso(d), name, nationwide: false });
  const inStates = (...codes: StateCode[]) => codes.includes(st);

  nat(utc(year, 1, 1), "Neujahr");
  nat(addDays(easter, -2), "Karfreitag");
  nat(addDays(easter, 1), "Ostermontag");
  nat(utc(year, 5, 1), "Tag der Arbeit");
  nat(addDays(easter, 39), "Christi Himmelfahrt");
  nat(addDays(easter, 50), "Pfingstmontag");
  nat(utc(year, 10, 3), "Tag der Deutschen Einheit");
  nat(utc(year, 12, 25), "1. Weihnachtstag");
  nat(utc(year, 12, 26), "2. Weihnachtstag");

  if (inStates("BW", "BY", "ST")) reg(utc(year, 1, 6), "Heilige Drei Könige");
  if ((st === "BE" && year >= 2019) || (st === "MV" && year >= 2023)) reg(utc(year, 3, 8), "Internationaler Frauentag");
  if (st === "BE" && (year === 2020 || year === 2025)) reg(utc(year, 5, 8), "Tag der Befreiung");
  if (st === "BB") {
    reg(easter, "Ostersonntag");
    reg(addDays(easter, 49), "Pfingstsonntag");
  }
  if (inStates("BW", "BY", "HE", "NW", "RP", "SL")) reg(addDays(easter, 60), "Fronleichnam");
  if (st === "SL") reg(utc(year, 8, 15), "Mariä Himmelfahrt");
  if (st === "TH" && year >= 2019) reg(utc(year, 9, 20), "Weltkindertag");
  const reformation: StateCode[] = ["BB", "MV", "SN", "ST", "TH"];
  if (year >= 2018) reformation.push("HB", "HH", "NI", "SH");
  if (year === 2017) nat(utc(year, 10, 31), "Reformationstag");
  else if (reformation.includes(st)) reg(utc(year, 10, 31), "Reformationstag");
  if (inStates("BW", "BY", "NW", "RP", "SL")) reg(utc(year, 11, 1), "Allerheiligen");
  if (st === "SN") reg(repentanceDay(year), "Buß- und Bettag");

  return list.sort((x, y) => x.date.localeCompare(y.date));
}

export function parseDate(value: string, field: string): Date {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  const d = m ? utc(Number(m[1]), Number(m[2]), Number(m[3])) : undefined;
  if (!d || iso(d) !== value) {
    throw new Error(`${field} '${value}' ist kein gültiges Datum. Erwartet wird JJJJ-MM-TT, z. B. 2026-12-24.`);
  }
  return d;
}

export function workingDays(start: Date, end: Date, state: string, saturdayIsWorkday = false) {
  if (end < start) throw new Error(`Das Enddatum ${iso(end)} liegt vor dem Startdatum ${iso(start)}.`);
  if (end.getTime() - start.getTime() > 366 * 5 * 86_400_000) {
    throw new Error("Der Zeitraum darf höchstens fünf Jahre umfassen.");
  }
  const byDay = new Map<string, Holiday>();
  for (let y = start.getUTCFullYear(); y <= end.getUTCFullYear(); y++) {
    for (const h of holidays(y, state)) byDay.set(h.date, h);
  }
  let count = 0;
  const skipped: Holiday[] = [];
  for (let d = start; d <= end; d = addDays(d, 1)) {
    const wd = d.getUTCDay(); // 0 = Sonntag
    const isWorkday = wd >= 1 && wd <= (saturdayIsWorkday ? 6 : 5);
    if (!isWorkday) continue;
    const h = byDay.get(iso(d));
    if (h) skipped.push(h);
    else count++;
  }
  return { count, skipped };
}
