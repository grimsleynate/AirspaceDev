import { AnsiUp } from "ansi_up";

const ansi = new AnsiUp();
ansi.use_classes = true;

export function ansiToHtml(value: string): string {
  return ansi.ansi_to_html(value.replace(/\r\n/g, "\n"));
}

export function looksLikePasswordPrompt(value: string): boolean {
  const tail = value.slice(-240);
  return /(?:enter|confirm|new|account).*\b(?:password|passphrase)\b|\b(?:password|passphrase)\b.*:/i.test(
    tail,
  );
}
