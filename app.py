from flask import Flask, render_template, request,redirect, url_for, flash, session
import re, os, shutil
from models import db, User

app = Flask(__name__)
app.secret_key = 'happy_happy_happy'  # Use a long, random string in production!
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webpersona.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
# Initialize the database (create tables if not exist)
with app.app_context():
    db.create_all()
 
class website:
    def __init__(self):
        self.size = "100%"
        self.sizes = ("100%",'320px','360px','390px','414px','480px','768px','820px','1024px','1280px','1440px','1536px','2560px')
        self.admin = "templates/adminPanel.html"
        self.folder = "templates/"
        self.extantion = ".html"
        self.pages = [page for page in os.listdir('templates/') if not os.path.isdir('templates/'+page) ]
        self.unremovablePages = ['Home.html','login.html','register.html']
        self.unviewPages = ['adminPanel.html','skeleton.html','Base.html']
        self.folders =  [page for page in os.listdir('templates/') if os.path.isdir('templates/'+page) and page!='Forms' ]
        self.folderDict = {folder : os.listdir("templates/"+folder) for folder in self.folders}
        self.favicons = os.listdir("static/favicons/")
        self.favicon = os.listdir("static/favicon/")
        self.previewPage = "/"
        self.logo = os.listdir("static/logo/")
        self.currentPage= str()
        self.themes = self.theme()
        self.len_of_theme_block = int()
        self.body_content_editable = False
        self.debugMode = False
        self.previewPageHtml = self.readSourceCode(self.previewPage)
        self.isLogedin = False
        self.isRegistered = False

    def theme(self):
        file = open("static/root.css", "r")
        return file.readlines()
            
    def readSourceCode(self,page):
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

        for i in blocks:
            len_of_theme_block = len(i)
            break
        # Flatten blocks back to lines
        newLines = [line for block in blocks for line in block]

        with open("static/root.css", "w", encoding="utf-8") as file:
            file.writelines(newLines)

        self.themes = self.theme()
        return len_of_theme_block
    
    def make_content_editabele(self):
        if self.body_content_editable == False:
            self.body_content_editable = True
            return 'On'
        else:
            self.body_content_editable = False
            return 'Off'
            

    def addPage(self, name, title,HTML):  
        # Create the page file if it doesn't exist
        if '.' in name:
            name = name[:name.find('name')]
        if '" "' in name:
            for i,d in enumerate(name):
                if d== "' '":
                    name[i] = name[i].replace(old='" "',new="_")
                    
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
        else:
            return FileExistsError(name)
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
        if fsize not in w.sizes and FrameSize > 0:
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
    
    def write_code_to_page(self,page,content,type, position=None):
        with open(page,'r') as file:
            lines = file.readlines()
        with open(page, "w") as f:
            if type=='img':
                c = "\n<img src='" + content+"' alt='Image...'/>\n"
                lines.insert(len(lines)-4,c)
                f.writelines(lines)
        
    
    def setImgInPage(self,imgPath, page,position=None):
        self.write_code_to_page(page, imgPath, 'img')
        
        
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
        print(oldblock)
        
        # 5. Replace line-by-line
        new = []
        jinja_pattern = r'{[{%#].*?[}%]}'  # Matches all Jinja tag types

        for a, line in enumerate(oldblock):
            if a >= len(html):
                break
            
            updated_line = html[a]
            
            if "<!--NO-->" in line:
                new.append(line)  # Preserve line
                print('preserved')
                
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
        print(new)
        with open('templates/'+file, 'w',encoding='utf-8') as f:
            f.writelines(final)
            
        
    def remove_last_n_lines(self,filepath, n):
        with open(filepath, 'r+b') as f:
            f.seek(0, os.SEEK_END)  # Move to the end of the file
            end = f.tell()

            count = 0
            while f.tell() > 0:
                f.seek(-1, os.SEEK_CUR)  # Move back one byte
                char = f.read(1)

                if char == b'\n':
                    count += 1
                    if count == n + 1:  # Count an extra newline to find the start of the line to keep
                        f.truncate()
                        print(f"Removed {n} lines from the end of the file.")
                        return 1
                    
                f.seek(-1, os.SEEK_CUR) # Move back again to process the previous byte
                
    def addLogic(self, path):
        with open(path,'r') as f:
            newLogic = f.readlines()
        
        with open("app.py",'r') as f:
            data = f.readlines()
            frrom = data.index('#New Logic\n')
            till = len(data)
            n = till - frrom-1
            suffix = data[frrom:till]
        
        self.remove_last_n_lines("app.py",n)
        
        with open('app.py','a') as file:
            file.writelines(newLogic+suffix)
        
            
w =website()

@app.route('/')
def Home():
    w.currentPage = "Home.html"
    return render_template('Home' + w.extantion, all=w.__dict__ ,web=w)

@app.route('/admin')
def admin():
    w.currentPage = "adminPanel.html"
    return render_template("adminPanel.html",  all=w.__dict__,web=w)
        
        
@app.route('/pageAddition', methods=['POST'])
def page_addition():
    name = request.form.get("fileName")
    title = request.form.get('title')
    HTML = request.files['ownHtml']
    if HTML and HTML.filename:
        if HTML.filename.endswith('.py'):
            fpath = os.path.join('../webpersona',HTML.filename)
            if os.path.exists(fpath):
                M='Rename the Python File'
                C = 'info'
            else:
                HTML.save(fpath)
                w.addLogic(fpath)
                M = "Backend logic saved succesfully" 
                C='success'
        else:
            fpath = os.path.join('templates',HTML.filename)
            if not os.path.exists(fpath):
                HTML.save(fpath) 
                M = f'Your page {HTML.filename} added succesfully !'
                C= 'success'
                w.pages = [page for page in os.listdir(w.folder) if not os.path.isdir(w.folder+page)]
            else:
                M= f'{HTML.filename} already exist'
                C = 'info'
        flash(M,C)
        
    elif name and title:
        result = w.addPage(name, title, HTML)
        if isinstance(result, Exception):
            flash(str(result), 'danger')
        else:
            flash('Page added successfully!', 'success')
    elif (not name or not title):
        flash('Seems you have not typed Page Name or Title','danger')
    
    return redirect(url_for('admin'))
    
@app.route('/faviconAddition', methods =['POST'])
def image_edition():
    icon = request.files["icon_path"]
    iconPath = os.path.join("static/favicons", icon.filename)
    try:
        icon.save(iconPath)
        w.favicons = os.listdir("static/favicons")
        flash("Favicon added successfully!", "success")
    except Exception as e:
        flash(f"Error adding favicon: {e}", "danger")
    return redirect(url_for('admin'))

@app.route('/frameSizeChange', methods = ['POST'])
def responsiveness(): 
    size = request.form.get('frame_size')
    result = w.changeFrameSize(size)
    if result == 1:
        flash('Frame size changed successfully!', 'success')
    else:
        flash('Frame size added!', 'info')
    return redirect(url_for('admin'))

@app.route('/delete-change-Favicon-page',methods=['POST'])
def operation_with_img_files():
    pathToDelete = request.form.get('delete_favicon')
    pathToChange = request.form.get('change_favicon')
    pathToDelPage = request.form.get('delete_page')
    pathForPreview = request.form.get('preview_page')
    pathTochangeLogo = request.form.get('change_logo')
    pathToSetinPage = request.form.get('set_to_page')
   
    if pathToDelete:
        try:
            w.deleteFile("static/favicons/" + pathToDelete)
            flash("Favicon deleted successfully!", "success")
        except Exception as e:
            flash(f"Error deleting favicon: {e}", "danger")
    if pathToChange:
        try:
            w.addFavicon("static/favicons/" + pathToChange)
            flash("Favicon changed successfully!", "success")
        except Exception as e:
            flash(f"Error changing favicon: {e}", "danger")
    if pathToDelPage:
        try:
            w.deleteFile("templates/" + pathToDelPage)
            flash("Page deleted successfully!", "success")
        except Exception as e:
            flash(f"Error deleting page: {e}", "danger")
    if pathForPreview:
        print('last : ', w.previewPage) 
        w.previewPage = pathForPreview
        print('current : ', w.previewPage)
        w.previewPageHtml = w.readSourceCode(w.previewPage)
        flash(f"Preview page set to {pathForPreview}", "info")
    if pathTochangeLogo:
        try:
            w.changeLogo("static/favicons/" + pathTochangeLogo)
            flash("Logo changed successfully!", "success")
        except Exception as e:
            flash(f"Error changing logo: {e}", "danger")
    
    if pathToSetinPage:
        try:
            w.setImgInPage(page="templates/"+w.previewPage,imgPath="static/favicons/"+pathToSetinPage)
            flash("Image set successfully!", "success")
        except Exception as e:
            flash(f"Error stting image: {e}", "danger")
            
    return redirect(url_for('admin'))

@app.route('/theme-rotate', methods=['POST'])
def rotate_theme():
    direction = request.form.get('change_theme')

    if direction in ['left', 'right']:
        n = w.changeTheme(direction)
        if n:
            flash(f"Theme changed: {direction}", "success")
            w.len_of_theme_block = n
        else: 
            flash(f"Something happened wrong", 'danger')
    return redirect(url_for('admin'))

@app.route("/Content-editable", methods=["POST"])
def contetn_editable():
    result = w.make_content_editabele()
    if w.previewPage == '/':
        w.previewPage = 'Home.html'
    if result == 'On':
        flash('Content edit mode On.', 'success')
    elif result == 'Off':
        flash('Content edit mode Off.', 'info')
    else:
        flash(f'{Exception}','danger')
        
    return redirect(url_for('admin'))

@app.route('/Debug-mode', methods=['POST'])
def debug_mode_change():
    if w.previewPage == '/':
        w.previewPage = 'Home.html'
        
    w.debugMode = not w.debugMode
    flash('Debug mode toggled.', 'info')
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
    try:
        w.edit_content(file, block_id, html)
        M = 'Edited block saved successfully!'
        C = 'success'
        print('done')
        
    except Exception as e:
        M = f'Error saving content block: {e}' 
        C = 'error'
        print(e)
        
    flash(M,C)
    return redirect(url_for('admin'))

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        address = request.form.get('address')
        password = request.form.get('password')
        # Check if user already exists
        if User.query.filter((User.email == email) | (User.mobile == mobile)).first():
            flash('Email or mobile already registered.', 'danger')
            return render_template('register.html')
        user = User(name=name, email=email, mobile=mobile, address=address, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please sign in.', 'success')
        w.isRegistered = True
        return redirect(url_for('login'))
    
    w.currentPage = 'register.html'
    return render_template('register.html', web=w, all=w.__dict__)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            w.isLogedin = True
            return redirect(url_for('Home'))
        else:
            flash('Invalid credentials.', 'danger')
    
    w.currentPage = 'login.html'
    return render_template('login.html', all=w.__dict__, web=w)

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'info')
    w.isLogedin = False
    return redirect(url_for('login'))

#New Logic
@app.route('/<name>')
def render_page(name):
    if name not in ["Home.html", "adminPanel.html"]:
        w.currentPage = name
        try:
            try:
                return render_template(f'Mini-pages/{name}', all=w.__dict__)
            except:
                return render_template(f"partials/{name}", all=w.__dict__)
        except:
            return render_template(f"{name}", all=w.__dict__)
    else:
        print("dynamic-n")
        if name == "Home.html":
            return redirect(url_for('Home'))
        else:
            return redirect(url_for('admin'))
            
if __name__ == "__main__":
    app.run(debug=True)