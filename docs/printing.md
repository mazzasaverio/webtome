# Printing your volumes

`webtome build` produces an interior PDF at **6"×9" (152×229 mm)** trim, the
most common paperback size, with mirrored margins (0.875" inside, 0.625"
outside) and no bleed. Text-only interiors do not need bleed; margins are
within the requirements of the major print-on-demand services.

## Option 1: home or office printer

- Print double-sided ("flip on long edge").
- Either print 2-up on A4/Letter and cut, or print 1-up centered and trim, or
  simply read it as a stapled/ring-bound stack.

## Option 2: local print shop

Ask for: *perfect bound (or coil bound), 6×9 inches, black and white interior,
cream 80 gsm paper, double-sided*. Hand them `dist/volume-NN.pdf`.

## Option 3: print-on-demand (one copy is fine)

[Lulu](https://www.lulu.com/) is the most webtome-friendly service: you can
print a single private copy without publishing anything. Rough steps:

1. Start a print book project, trim size **6×9 in (US Trade)**.
2. Upload `dist/volume-NN.pdf` as the interior. Choose black-and-white on
   cream for essay collections.
3. Make a cover with their online tool or upload one (see below).
4. Order your copy. Do **not** enable distribution: these books contain other
   people's articles and are for personal use only.

Amazon KDP also accepts 6×9 interiors, but KDP is oriented toward *selling*
books; for personal anthologies prefer Lulu or a local shop.

### Page count limits

Perfect binding needs a minimum page count (Lulu: 32; KDP: 24) and tops out
around 800 pages. `webtome status` shows articles per volume; if a build comes
out too thin, wait for more articles, too thick, split into two volumes.

### Covers

The interior PDF is only the inside of the book. Print-on-demand services want
a separate one-piece cover PDF (back + spine + front) whose spine width
depends on the final page count. Both Lulu and KDP provide calculators and
templates; a cover generator is on the webtome roadmap.

## Copyright, plainly

Printing web articles for yourself is personal-use archiving, like printing
from your browser. Selling or distributing them is not. Keep volumes private;
webtome stamps every chapter with its source URL and appends a full source
list so attribution always travels with the paper.
