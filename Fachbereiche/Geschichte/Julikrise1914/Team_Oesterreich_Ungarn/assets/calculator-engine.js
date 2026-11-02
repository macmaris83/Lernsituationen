(function (root, factory) {
  const Calculator = factory();
  if (typeof module === 'object' && module.exports) module.exports = {Calculator};
  else root.BBSCalculator = Calculator;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const operators = new Set(['+', '-', '*', '/']);
  const clean = value => {
    if (!Number.isFinite(value)) throw new Error('Zahl zu groß');
    return Object.is(value, -0) ? '0' : String(Number(value.toPrecision(14)));
  };
  const apply = (a, operator, b) => {
    if (operator === '/' && b === 0) throw new Error('Division durch null');
    const value = operator === '+' ? a + b : operator === '-' ? a - b : operator === '*' ? a * b : a / b;
    if (!Number.isFinite(value)) throw new Error('Zahl zu groß');
    return value;
  };
  function evaluate(tokens) {
    const terms = [tokens[0]], low = [];
    for (let i = 1; i < tokens.length; i += 2) {
      const op = tokens[i], value = tokens[i + 1];
      if (op === '*' || op === '/') terms[terms.length - 1] = apply(terms[terms.length - 1], op, value);
      else { low.push(op); terms.push(value); }
    }
    return terms.slice(1).reduce((sum, term, i) => apply(sum, low[i], term), terms[0]);
  }
  class Calculator {
    constructor(saved) {
      this.reset();
      if (saved && typeof saved.entry === 'string' && /^-?\d+(?:\.\d*)?(?:e[+-]?\d+)?$/i.test(saved.entry)
          && saved.entry.length < 50 && Number.isFinite(Number(saved.entry)) && Array.isArray(saved.tokens) && saved.tokens.length <= 64 && saved.tokens.length % 2 === 0
          && saved.tokens.every((value, i) => i % 2 ? operators.has(value) : typeof value === 'number' && Number.isFinite(value))) {
        this.entry = saved.entry; this.tokens = saved.tokens.slice(); this.awaiting = !!saved.awaiting;
        this.replace = !!saved.replace; this.finished = !!saved.finished;
        if (['Division durch null', 'Zahl zu groß'].includes(saved.error)) this.error = saved.error;
        if (saved.last && operators.has(saved.last.operator) && Number.isFinite(saved.last.value)) this.last = {...saved.last};
      }
    }
    reset() { this.entry = '0'; this.tokens = []; this.awaiting = false; this.replace = false; this.finished = false; this.last = null; this.error = ''; }
    snapshot() { return {entry:this.entry, tokens:this.tokens.slice(), awaiting:this.awaiting, replace:this.replace, finished:this.finished, last:this.last, error:this.error}; }
    get display() { return this.error ? 'Fehler' : this.entry.replace('.', ','); }
    get expression() { return this.tokens.map(x => typeof x === 'number' ? clean(x).replace('.', ',') : ({'*':'×','/':'÷','-':'−'}[x] || x)).join(' '); }
    press(key) {
      try {
        if (key === 'AC') { this.reset(); return; }
        if (/^[0-9.,]$/.test(key)) {
          if (this.error || this.finished) this.reset();
          if (this.awaiting || this.replace) { this.entry = '0'; this.awaiting = false; this.replace = false; }
          if (key === ',' || key === '.') { if (!this.entry.includes('.')) this.entry += '.'; }
          else if (this.entry.replace(/\D/g, '').length < 14) this.entry = this.entry === '0' ? key : this.entry === '-0' ? '-' + key : this.entry + key;
          return;
        }
        if (key === 'Backspace') {
          if (this.error) { this.reset(); return; }
          if (this.awaiting) return;
          this.entry = this.entry.slice(0, -1); if (!this.entry || this.entry === '-') this.entry = '0';
          this.finished = false; this.replace = false; return;
        }
        if (this.error) return;
        if (key === '±') {
          if (this.awaiting) { this.entry = '0'; this.awaiting = false; }
          this.entry = this.entry.startsWith('-') ? this.entry.slice(1) : '-' + this.entry;
          this.replace = false; return;
        }
        if (key === '%') {
          let value = Number(this.entry) / 100;
          if (!this.awaiting && ['+', '-'].includes(this.tokens.at(-1))) value *= evaluate(this.tokens.slice(0, -1));
          this.entry = clean(value); this.awaiting = false; this.replace = true; this.finished = false; return;
        }
        if (operators.has(key)) {
          if (this.finished) { this.tokens = []; this.finished = false; }
          if (this.awaiting) this.tokens[this.tokens.length - 1] = key;
          else {
            this.tokens.push(Number(this.entry), key);
            if (this.tokens.length > 60) this.tokens = [evaluate(this.tokens.slice(0, -1)), key];
          }
          this.awaiting = true; this.replace = false; return;
        }
        if (key === '=') {
          if (this.finished && this.last) this.entry = clean(apply(Number(this.entry), this.last.operator, this.last.value));
          else {
            const value = Number(this.entry);
            this.last = this.tokens.length ? {operator:this.tokens.at(-1), value} : null;
            this.entry = clean(evaluate([...this.tokens, value]));
          }
          this.tokens = []; this.awaiting = false; this.replace = true; this.finished = true;
        }
      } catch (error) { this.error = error.message; this.tokens = []; this.awaiting = false; this.finished = false; }
    }
  }
  return Calculator;
});
