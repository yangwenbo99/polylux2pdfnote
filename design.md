- Use the following for note with metadata: 
```typst
#let snote(begin: 1, end: -1, body) = [
  #metadata(
    (t: "SlideNote", begin: begin, end: end, body: repr(body))
  ) <pdfpc>
]
```
- `/home/yang/Downloads/Softs/typst/repr_fixed/typst/target/release/typst query --format json ./proposal_present_v2.typ '<slides-note>'`
- Remove the `[]` in the ouput value. 
- Use the following to show the output, or just parse using python
```typst
#{
  let a = json("aaa.json")
  let res = eval(a.at("value"), mode: "code")
  for i in range(res.len()) {
    res.at(i)
  }
}
```


