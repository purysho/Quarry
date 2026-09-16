from pathlib import Path
from PIL import Image, ImageDraw
BG='#0a120d'; A='#61d991'; B='#f0c95d'
def rgb(h):
    h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))+(255,)
img=Image.new("RGBA",(256,256),rgb(BG)); d=ImageDraw.Draw(img); A=rgb(A); B=rgb(B)
d.polygon([(32,64),(90,44),(150,48),(224,66),(224,100),(166,88),(95,88),(32,104)],fill=(23,59,40,255),outline=A); d.polygon([(32,110),(86,92),(151,92),(224,104),(224,138),(160,128),(95,130),(32,147)],fill=(33,76,51,255),outline=B); d.polygon([(32,154),(91,140),(154,142),(224,150),(224,192),(160,184),(95,184),(32,200)],fill=(42,92,61,255),outline=B); d.ellipse((161,66,191,96),fill=(240,201,93,255))
out=Path(__file__).resolve().parents[1]/"assets"/"icon.ico"
out.parent.mkdir(exist_ok=True)
img.save(out,format="ICO",sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
print(out)