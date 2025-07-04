from flask import Flask, render_template, request,redirect, url_for
import re, os, shutil
from jinja2 import Environment

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
class website:
    def __init__(self):
        self.size = "100%"
        self.sizes = ["100%",'320px','360px','390px','414px','480px','768px','820px','1024px','1280px','1440px','1536px','2560px']
        self.admin = "templates/adminPanel.html"
        self.folder = "templates/"
        self.extantion = ".html"
        self.pages = [page for page in os.listdir('templates/') if not os.path.isdir('templates/'+page) ]
        self.unremovablePages = ['Home.html']
        self.unviewPages = ['adminPanel.html','skeleton.html','Base.html']
        self.folders =  [page for page in os.listdir('templates/') if os.path.isdir('templates/'+page) ]
        self.folderDict = {folder : os.listdir("templates/"+folder) for folder in self.folders}
        self.favicons = os.listdir("static/favicons/")
        self.favicon = os.listdir("static/favicon/")
        self.previewPage = "/"
        self.logo = os.listdir("static/logo/")
        self.currentPage="Home.html"
        self.themes = self.theme()
        self.body_content_editable = False
        self.debugMode = False
        self.previewPageHtml = self.readSourceCode()

    def theme(self):
        file = open("static/root.css", "r")
        return file.readlines()
            
    def readSourceCode(self):
        page = self.previewPage
        if page == '/':
            return ["Select a Page!"]
        if page in self.folderDict['partials']:
            page = 'partials/'+page
            
        page = self.folder+page

        with open(page,'r',encoding='utf-8') as f:
            code = f.readlines()
        return code
        
    def changeTheme(self, direction):
        # Read all lines from root.css
        with open("static/root.css", "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Parse theme blocks: each starts with a comment (/* ThemeName */) and ends with '}'
        blocks = []
        current_block = []
        in_block = False
        for line in lines:
            if line.strip().startswith("/*") and line.strip().endswith("*/"):
                if current_block:
                    blocks.append(current_block)
                    current_block = []
                in_block = True
                current_block.append(line)
            elif in_block:
                current_block.append(line)
                if line.strip() == "}":
                    blocks.append(current_block)
                    current_block = []
                    in_block = False
        # In case file doesn't end with a newline
        if current_block:
            blocks.append(current_block)

        # Remove any empty blocks
        blocks = [b for b in blocks if any(l.strip() for l in b)]

        # Rotate blocks
        if len(blocks) > 1:
            if direction == 'right':
                blocks = blocks[1:] + [blocks[0]]
            elif direction == 'left':
                blocks = [blocks[-1]] + blocks[:-1]

        # Flatten blocks back to lines
        newLines = [line for block in blocks for line in block]

        with open("static/root.css", "w", encoding="utf-8") as file:
            file.writelines(newLines)

        self.themes = self.theme()
        return redirect('/admin')
    
    def make_content_editabele(self):
        if self.body_content_editable == False:
            self.body_content_editable = True
        else:
            self.body_content_editable = False
            

    def addPage(self, name, title,HTML):  
        # Create the page file if it doesn't exist
       
        file_path = self.folder + name + self.extantion
        if not os.path.exists(file_path):
            with open("templates/Base.html", "r") as base:
                baseF = base.readlines()
                for i,line in enumerate(baseF):
                    if "<!--title-->" in line:
                        baseF[i] = baseF[i].replace("<!--title-->",title) 
                        break
            with open('templates/partials/body.html','r') as body:
                bodyF = body.readlines()
                for i,line in enumerate(bodyF):
                    if 'write_id' in line:
                        bodyF[i] = bodyF[i].replace('write_id', name+'.html')
                        break
            with open(file_path,'w') as file:
                if HTML:
                    file.write(str(baseF)+HTML)
                else:
                    file.writelines(baseF+bodyF)
                      
        self.pages = [page for page in os.listdir(self.folder) if not os.path.isdir(self.folder+page) ]
        
    def addFavicon(self,icon_path):
        if len(self.favicon) < 1:
            shutil.copy(icon_path,"static/favicon/")
        else:
            if os.path.exists("static/favicons/"+self.favicon[0]):
                os.remove("static/favicons/"+self.favicon[0])
            shutil.move("static/favicon/"+self.favicon[0], "static/favicons/")
            shutil.copy(icon_path,"static/favicon/")
        self.favicon = os.listdir("static/favicon/")
        self.favicons = os.listdir("static/favicons")
        print(self.favicon)
        print(self.favicons)
        
    def changeFrameSize(self,FrameSize):
        if FrameSize in self.sizes:
            self.size = FrameSize
            return 1
            
        fsize = str(FrameSize)+"px"
        if fsize not in w.sizes and FrameSize>0:
            self.sizes.append(fsize)
            self.size = fsize
            print(self.size)
        
    def deleteFile(self,path):
        os.remove(path) 
        self.favicons = os.listdir("static/favicons")
        self.pages = [page for page in os.listdir('templates/') if not os.path.isdir('templates/'+page) ] 
        self.pages.remove('adminPanel.html')
        
    def changeLogo(self,path):
        if len(self.logo) < 1:
            shutil.copy(path,"static/logo/")
        else:
            if os.path.exists("static/favicons/"+self.logo[0]):
                os.remove("static/favicons/"+self.logo[0])
            shutil.move("static/logo/"+self.logo[0], "static/favicons/")
            shutil.copy(path,"static/logo/")
        self.logo = os.listdir("static/logo/")
        self.favicons = os.listdir("static/favicons")
    
    def edit_content(self, file, block_id, html):
        while html[0] == '' or html[0] == "<!--start-->\n":
            html.pop(0)
        while html[len(html)-1]=='':
            html.pop(len(html)-1)
            
        print(html)
        with open('templates/'+file, "r", encoding="utf-8") as f:
            content = f.readlines()
            
        pattern = fr'(<[^>]+id=["\']{block_id}["\'][^>]*>)'

        # 1. Find start of block 
        start_idx = None
        for i, line in enumerate(content):
            if re.match(pattern, line) or "<!--start-->" in line:
                start_idx = i
                break

        if start_idx is None:
            raise ValueError("Start tag not found")
        
        # 2. Find end of block
        end_idx = None
        for i in range(len(content)-1,1,-1):
            if '<!--Close-->' in content[i]:
                end_idx = i
                break

        if end_idx is None:
            raise ValueError("Closing tag not found")

        # 3. Prepare prefix and suffix
        prefix = content[:start_idx + 1]
        suffix = content[end_idx:]
    
        # 4. Extract block to replace
        oldblock = content[start_idx + 1:end_idx]
     
        # 5. Replace line-by-line
        new = []
        jinja_pattern = r'{[{%#].*?[}%]}'  # Matches all Jinja tag types

        for a, line in enumerate(oldblock):
            if a >= len(html):
                break

            updated_line = html[a]

            if "<!--NO-->" in line:
                new.append(line)  # Preserve line
            elif re.search(jinja_pattern, line.strip()):
                jinja_match = re.search(jinja_pattern, line)
                if jinja_match:
                    preserved = jinja_match.group()
                    # inject Jinja back into updated line
                    rebuilt = ''
                    i = 0
                    once = True
                    for l in updated_line:
                        if line[i] != '{':
                            rebuilt +=  l
                        elif line[i] == '{' and once==True:
                            rebuilt += line[line.find('{'):line.rfind('}')+1]
                            g = line.rfind('}')-line.find('{')
                            once = False
                        i=i+1
                    
                    half_1 = rebuilt[:rebuilt.rfind('}')+1]
                    half_2 = rebuilt[rebuilt.rfind('}')+1:]
                
                    for t in half_2:
                        if t == '"':
                            break
                        elif t != '"':
                            half_2 = half_2.removeprefix(t)

                    rebuilt = half_1+half_2
                    new.append(rebuilt)        
                    
                else:
                    new.append(updated_line)        
            else:
                new.append(updated_line)
                
        final = prefix+new+suffix
        
        with open('templates/'+file, 'w',encoding='utf-8') as f:
            f.writelines(final)
        
w =website()
print(w.folderDict)
@app.route('/')
def interface():
    print(w.currentPage)
    print(w.body_content_editable)
    return render_template('home' + w.extantion, all=w.__dict__ ,web=w)

@app.route('/admin')
def admin():
    w.currentPage = "adminPanel.html"
    print(w.currentPage)
    print(w.body_content_editable)

    return render_template("adminPanel.html",  all=w.__dict__,web=w)
        
        
@app.route('/pageAddition', methods=['POST'])
def fuc():
    name = request.form.get("fileName")
    title = request.form.get('title')
    HTML = request.form.get('ownHtml')
    w.addPage(name,title,HTML)
    return render_template("adminPanel.html", all=w.__dict__)
    
@app.route('/faviconAddition', methods =['POST'])
def fuc2():
    icon= request.files["icon_path"]
    iconPath = os.path.join("static/favicons",icon.filename)
    icon.save(iconPath)
    w.favicons = os.listdir("static/favicons")
    print("done")
    
    return render_template("adminPanel.html", all=w.__dict__)

@app.route('/frameSizeChange', methods = ['POST'])
def fuc3(): 
    size = request.form.get('frame_size')
    w.changeFrameSize(size)
    
    return redirect(url_for('admin'))

@app.route('/delete-change-Favicon-page',methods=['POST'])
def fuc4():
    pathToDelete = request.form.get('delete_favicon')
    pathToChange = request.form.get('change_favicon')
    pathToDelPage = request.form.get('delete_page')
    pathForPreview = request.form.get('preview_page')
    pathTochangeLogo = request.form.get('change_logo')
   
    if pathToDelete:
        w.deleteFile("static/favicons/"+pathToDelete)
    if pathToChange:
        w.addFavicon("static/favicons/"+pathToChange)
    if pathToDelPage:
        w.deleteFile("templates/"+pathToDelPage)
    
    if pathForPreview:
        print('last : ',w.previewPage)
        w.previewPage = pathForPreview
        print('current : ',w.previewPage)
    
    if pathTochangeLogo:
        w.changeLogo("static/favicons/"+pathTochangeLogo)
        
    return redirect(url_for('admin'))

@app.route('/theme-rotate', methods=['POST'])
def rotate_theme():
    direction = request.form.get('change_theme')

    if direction in ['left', 'right']:
        w.changeTheme(direction)
        print("Theme changed:", direction)

    return redirect(url_for('admin')) 

@app.route("/Content-editable", methods=["POST"])
def fuc7():
    w.make_content_editabele()
    return redirect(url_for('admin'))

@app.route('/Debug-mode', methods=['POST'])
def debug_mode_change():
    w.debugMode = True if w.debugMode==False else False
    w.previewPageHtml = w.readSourceCode()
    return redirect(url_for('admin'))
    
@app.route('/save-block-multi', methods=['POST'])
def save_block_multi():
    print('saving on')
    data = request.get_json()
    file = data.get("file")
    if data.get('file') in w.folderDict['partials']:
        file = "partials/" + file

    block_id = data.get("block")
    html = data.get("html")
    w.edit_content(file,block_id,html)

    return redirect(url_for('admin'))


@app.route('/<name>')
def render_page(name):
    if name not in ["Home.html", "adminPanel.html"]:
      
        print("dynamic")
        try:
            return render_template(f"partials/{name}", all=w.__dict__)
        except:
            pass
        w.currentPage = name 
        return render_template(f"{name}", all=w.__dict__)
    else:
        print("dynamic-n")
        if name == "Home.html":
            return redirect(url_for('interface'))
        else:
            return redirect(url_for('admin'))
            

if __name__ == "__main__":
    app.run(debug=True)


