"""Re-pack an edited x-dc template into a claude.ai/design single-file bundle.
Usage: bundle.py <original_bundle.html> <edited_template.html> <out.html>
Only the __bundler/template island changes; manifest (fonts, React, runtime) is reused byte-for-byte."""
import re,json,sys
def enc(d):
    return '\n'+json.dumps(d,ensure_ascii=False).replace('</', '<\\u002F')+'\n  '
def split(s):
    m=re.search(r'(<script type="__bundler/template">)(.*?)(</script>)',s,re.S); return m
if __name__=='__main__':
    src,tpl,out=sys.argv[1:4]
    s=open(src).read(); m=split(s)
    new=s[:m.start(2)]+enc(open(tpl).read())+s[m.end(2):]
    open(out,'w').write(new)
