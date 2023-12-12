A tool for generating polylux presentation with presentor note in the same way as beamer's. 

The difference from polylux's pdfpc support is that this note supports typst syntax. 

## Usage

First, *put the following code in your typst file*: 
```typst
#let snote(begin: 1, end: -1, body) = [
  #let res = (t: "SlideNote", begin: begin, end: end, body: repr(body))
  #if body.has("lang") {
    res.insert("lang", body.at("lang"))
  }
  #if body.has("text") {
    res.insert("text", body.at("text"))
  }
  #metadata(
    // json.encode((begin: begin, end: end, body: body))
    // json.encode(body)
    res
  ) <pdfpc>
]
```

Then, write your note in the presentation source file. 
The tool currently support two types of notes: 
~~~typst
// type 1
#snote[Simple note]

// type 2
#snote(```typst
  Complex note
  #set text(size: 18pt)
  - Item 1
  - Item 2
  ```
)
~~~
The second type is necessary, due to the issues with Typst's `repr()` ([link](https://github.com/typst/typst/pull/2896)). 

Finally, execute the Python script.  The python code is self-documentary.  An example: 

```bash
polylux2pdfnote.py --typst 'your/path/to/typst/executable' --preamble present_preamble.typ join present.typ --compress
```



## Limitations

- Over-length slides (except the reference slides) not supported. 
- Hyperlink will be lost
- [A patched version of Typst](https://github.com/astrale-sharp/typst/tree/content-repr-2887) needs to be used.  (Hopefully, it will be merged very soon.)

