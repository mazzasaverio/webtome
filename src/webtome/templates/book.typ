// webtome book template
// Print-ready interior: 6in x 9in trim, mirrored margins, no bleed
// (text-only interiors do not need bleed on KDP/Lulu).

#let chapter(title: "", author: none, source: none, date: none, body) = {
  pagebreak(weak: true, to: "odd")
  heading(level: 1, title)
  {
    set text(size: 8.5pt, fill: luma(35%))
    set par(first-line-indent: 0em)
    let parts = ()
    if author != none { parts.push(emph(author)) }
    if date != none { parts.push(date) }
    block(above: 0.6em, below: 0.4em, parts.join([ #h(4pt) · #h(4pt) ]))
    if source != none {
      block(below: 1.8em, raw(source))
    } else {
      v(1.4em)
    }
  }
  {
    set heading(offset: 1)
    body
  }
}

#let part(title) = {
  pagebreak(weak: true, to: "odd")
  set page(header: none, footer: none)
  v(30%)
  align(center)[
    #heading(level: 1, outlined: true, title)
  ]
  pagebreak()
}

#let sources-page(entries) = {
  pagebreak(weak: true, to: "odd")
  heading(level: 1, "Sources")
  set text(size: 8.5pt)
  set par(first-line-indent: 0em, justify: false)
  for (title, url) in entries {
    block(below: 0.9em)[#emph(title)\ #raw(url)]
  }
}

#let book(
  title: "Collected Articles",
  subtitle: none,
  curator: none,
  date: none,
  body,
) = {
  set document(title: title)
  set page(
    width: 6in,
    height: 9in,
    margin: (inside: 0.875in, outside: 0.625in, top: 0.75in, bottom: 0.8in),
  )
  set text(size: 10.5pt, lang: "en")
  set par(justify: true, leading: 0.62em, first-line-indent: 1.1em, spacing: 0.62em)

  show heading.where(level: 1): it => {
    set text(size: 17pt, weight: "bold")
    set par(first-line-indent: 0em)
    v(4em)
    it
  }
  show heading.where(level: 2): it => {
    set text(size: 12pt, weight: "bold")
    block(above: 1.6em, below: 0.8em, it)
  }
  show heading.where(level: 3): it => {
    set text(size: 10.5pt, weight: "bold", style: "italic")
    block(above: 1.4em, below: 0.7em, it)
  }
  show link: it => it.body
  show quote.where(block: true): set pad(x: 1.5em)

  // --- Title page -------------------------------------------------------
  {
    set page(footer: none)
    v(28%)
    align(center)[
      #text(size: 24pt, weight: "bold")[#title]
      #if subtitle != none {
        v(1.2em)
        text(size: 14pt)[#subtitle]
      }
      #v(1fr)
      #if curator != none { text(size: 11pt)[Curated by #curator] }
      #if date != none {
        v(0.6em)
        text(size: 10pt, fill: luma(35%))[#date]
      }
      #v(12%)
    ]
    pagebreak()
  }

  // --- Colophon ---------------------------------------------------------
  {
    set page(footer: none)
    set text(size: 8.5pt, fill: luma(30%))
    set par(first-line-indent: 0em, justify: false)
    v(1fr)
    [
      This volume is a personal anthology of articles collected from the web,
      assembled for private reading with webtome
      (#raw("https://github.com/mazzasaverio/webtome")).
      All articles remain the property of their respective authors; the
      original source of each piece is noted on its opening page and listed
      at the end of the book. Not for sale or redistribution.
    ]
    pagebreak()
  }

  // --- Table of contents ------------------------------------------------
  {
    set page(footer: none)
    set par(first-line-indent: 0em)
    show outline.entry: set block(above: 0.9em)
    outline(title: [Contents], depth: 1)
    pagebreak(to: "odd")
  }

  // --- Main matter ------------------------------------------------------
  set page(
    numbering: "1",
    footer: context align(center, text(size: 9pt, counter(page).display("1"))),
  )
  counter(page).update(1)
  body
}
