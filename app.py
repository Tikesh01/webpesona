from flask import Flask, render_template, request,redirect, url_for, flash, session, send_from_directory
import re, os, shutil, json
from models import db, User

app = Flask(__name__)
app.secret_key = 'happy_happy_happy' 
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webpersona.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
 
class website:
    def __init__(self):
        self.admin = "templates/adminPanel.html"
        self.folder = "templates/"
        self.extantion = ".html"
        self.pages = [page for page in os.listdir('templates/') if not os.path.isdir('templates/'+page)]
        self.unremovablePages = ['home.html','login.html','register.html']
        self.unviewPages = ['adminPanel.html','skeleton.html','Base.html']
        self.folders = [folder for folder in os.listdir('templates/') if os.path.isdir('templates/'+folder) and folder!='Forms']
        self.folderDict = {folder: os.listdir("templates/"+folder) for folder in self.folders}
        self.favicons = os.listdir("static/favicons/")
        self.favicon = os.listdir("static/favicon/")
        self.logo = os.listdir("static/logo/")
        self.header_pages = [page for page in os.listdir('templates/Header_pages/')]
        self.themes = self.theme()
        self.len_of_theme_block = int()

        try:
            with open("static/web.json", "r") as wjs:
                web_dict = json.load(wjs)
    
                self.size = web_dict.get("size", "100%")
                self.sizes = list(web_dict.get("sizes", ["100%","320px","360px","390px","414px","480px","768px","820px","1024px","1280px","1440px","1536px","2560px"]))
                self.previewPage = web_dict.get("previewPage", "Home.html")
                self.currentPage = web_dict.get("currentPage", "")
                self.body_content_editable = web_dict.get("body_content_editable", False)
                self.debugMode = web_dict.get("debugMode", False)
                self.isLogedin = web_dict.get("isLogedin", False)
                self.isRegistered = web_dict.get("isRegistered", False)
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            flash(f"Warning: Could not load web.json: {e}")
    
            self.size = "100%"
            self.sizes = ["100%","320px","360px","390px","414px","480px","768px","820px","1024px","1280px","1440px","1536px","2560px"]
            self.previewPage = "Home.html"
            self.currentPage = str()
            self.body_content_editable = False
            self.debugMode = False
            self.isLogedin = False
            self.isRegistered = False

            self.save_state()

        try:
            with open("static/navigation.json", "r") as nav_file:
                nav_dict = json.load(nav_file)
                self.navigation = [{"name": key, "value": value} for key, value in nav_dict.items()]
        except (FileNotFoundError, json.JSONDecodeError):
            self.navigation = []

        self.previewPageHtml = self.readSourceCode(self.previewPage)

    def save_state(self):
        """Save current state to web.json"""
        state = {
            "size": self.size,
            "sizes": list(self.sizes),
            "previewPage": self.previewPage,
            "currentPage": self.currentPage,
            "body_content_editable": self.body_content_editable,
            "debugMode": self.debugMode,
            "isLogedin": self.isLogedin,
            "isRegistered": self.isRegistered
        }
        try:
            with open("static/web.json", "w") as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            flash(f"Warning: Could not save state to web.json: {e}", 'dangour')
            
    def theme(self):
        file = open("static/root.css", "r")
        return file.readlines()
            
    def readSourceCode(self,page):
        if page == '/':
            return ["Select a Page!"]
        if page in self.folderDict['partials']:
            page = 'partials/'+page
        if page in self.folderDict['Header_pages']:
            page = 'Header_pages/'+page
            
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
    
    def make_content_editable(self):
        if self.body_content_editable == True:
            self.body_content_editable = False
            result = 'On'
        else:
            self.body_content_editable = True
            result = 'Off'
        self.save_state()
        return result
            

    def addPage(self, name, title,HTML):  
        if '.' in name:
            name = os.path.splitext(name)[0]
        if " " in name:
            for i,d in enumerate(name):
                if d== " ":
                    name[i] = name[i].replace(old=" ",new="_")
                    
        file_path = self.folder + name + self.extantion
        partials = self.folder+'partials/'+name+self.extantion
        if not os.path.exists(file_path) and not  os.path.exists(partials):
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
            self.save_state()
            return 1
            
        fsize = str(FrameSize)+"px"
        if fsize not in w.sizes and FrameSize > 0:
            self.sizes.append(fsize)
            self.size = fsize
            self.save_state()
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
        for folder in self.folderDict.keys():
            print(folder, self.folderDict[folder])
            if page in self.folderDict[folder]:
                page = f"{folder}/"+page
                break
        page = 'templates/'+page 
        with open(page,'r') as file:
            lines = file.readlines()
            print(lines)
        with open(page, "w") as f:
            if type=='img':
                c = "\t\t\t<img src='" + content+"' alt='Image...'/>\n"
                lines.insert(len(lines)-4,c)
                f.writelines(lines)
            if 'element':
                cleaned = "\n".join(line for line in content.splitlines() if line.strip() != "")
                lines.insert(len(lines)-4, cleaned + "\n")
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

        start_idx = None
        for i, line in enumerate(content):
            if re.match(pattern, line) or "<!--start-->" in line:
                start_idx = i
                break

        if start_idx is None:
            raise ValueError("Start tag not found")
 
        end_idx = None
        for i in range(len(content)-1,1,-1):
            if '<!--Close-->' in content[i]:
                end_idx = i
                break

        if end_idx is None:
            raise ValueError("Closing tag not found")

        prefix = content[:start_idx + 1]
        suffix = content[end_idx:]
    
        oldblock = content[start_idx + 1:end_idx]
        print(oldblock)
        
        new = []
        jinja_pattern = r'{[{%#].*?[}%]}'  

        for a, line in enumerate(oldblock):
            if a >= len(html):
                break
            
            updated_line = html[a]
            
            if "<!--NO-->" in line:
                new.append(line) 
                print('preserved')
                
            elif re.search(jinja_pattern, line.strip()):
                jinja_match = re.search(jinja_pattern, line)
                if jinja_match:
                    preserved = jinja_match.group()
                    
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
    
    w.currentPage = "home.html"
    return render_template('home.html', all=w.__dict__ ,web=w)

@app.route('/admin')
def admin():
    w.currentPage = "adminPanel.html"
    return render_template("adminPanel.html",  all=w.__dict__,web=w)
        
        
@app.route('/Addition', methods=['POST'])
def addition():
    name = request.form.get("fileName")
    title = request.form.get('title')
    # HTML = request.files['ownHtml']
    navText = request.form.get('navigationText')
    navTextPos = request.form.get('navigationTextPos')
    navPage = request.form.get('navigationPage')
    try:
        if navText and navPage:
            with open("static/navigation.json", "r") as js:
                nav_dict = json.load(js)
            nav_items = list(nav_dict.items())
            new_item = (navText, navPage)
            if navTextPos:
                try:
                    pos = int(navTextPos) - 1
                    nav_items.insert(pos, new_item)
                except Exception:
                    nav_items.append(new_item)
            else:
                nav_items.append(new_item)
            new_nav_dict = dict(nav_items)
            with open("static/navigation.json", "w") as Js:
                json.dump(new_nav_dict, Js, indent=4)
            w.navigation = [{"name": key, "value": value} for key, value in new_nav_dict.items()]
    except Exception as e:
        flash(f"Navigation update error: {e}", "danger")
            
    # if HTML and HTML.filename:
    #     if HTML.filename.endswith('.py'):
    #         fpath = os.path.join('../webpersona',HTML.filename)
    #         if os.path.exists(fpath):
    #             M='Rename the Python File'
    #             C = 'info'
    #         else:
    #             HTML.save(fpath)
    #             w.addLogic(fpath)
    #             M = "Backend logic saved succesfully" 
    #             C='success'
    #     else:
    #         fpath = os.path.join('templates',HTML.filename)
    #         if not os.path.exists(fpath):
    #             HTML.save(fpath) 
    #             M = f'Your page {HTML.filename} added succesfully !'
    #             C= 'success'
    #             w.pages = [page for page in os.listdir(w.folder) if not os.path.isdir(w.folder+page)]
    #         else:
    #             M= f'{HTML.filename} already exist'
    #             C = 'info'
    #     flash(M,C)
        
    # elif name and title:
    #     result = w.addPage(name, title,HTML)
    #     if isinstance(result, Exception):
    #         flash(str(result) +"already exist", 'danger')
    #     else:
    #         flash('Page added successfully!', 'success')
    # elif (not name or not title):
    #     flash('Seems you have not typed Page Name or Title','danger')
    
    return redirect(url_for('admin'))

@app.route('/Deletion', methods=['POST'])
def deletion():
    navToDel = request.form.get('delete_navigation')
    with open("static/navigation.json", "r") as js:
        nav_dict = json.load(js)

    print(navToDel, nav_dict.items())
    for dict_items in nav_dict.items():
        if navToDel in dict_items:
            del nav_dict[navToDel]
            with open("static/navigation.json", "w") as js:
                json.dump(nav_dict, js, indent=4)
            w.navigation = [{"name": key, "value": value} for key, value in nav_dict.items()]
            flash(f"Navigation item '{navToDel}' deleted successfully!", "success")
            break
            
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
    pathToSetInPage = request.form.get('set_to_page')
   
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
            w.previewPage = 'Home.html'
            flash("Page deleted successfully!", "success")
        except Exception as e:
            flash(f"Error deleting page: {e}", "danger")
    if pathForPreview:
        print('last : ', w.previewPage) 
        w.previewPage = pathForPreview
        print('current : ', w.previewPage)
        w.previewPageHtml = w.readSourceCode(w.previewPage)
        w.save_state()
        flash(f"Preview page set to {pathForPreview}", "info")
        
    if pathTochangeLogo:
        try:
            w.changeLogo("static/favicons/" + pathTochangeLogo)
            flash("Logo changed successfully!", "success")
        except Exception as e:
            flash(f"Error changing logo: {e}", "danger")
    
    if pathToSetInPage:
        try:
            w.setImgInPage(page="templates/"+w.previewPage,imgPath="static/favicons/"+pathToSetInPage)
            flash("Image set successfully!", "success")
        except Exception as e:
            flash(f"Error setting image: {e}", "danger")
            
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
    result = w.make_content_editable()
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
        w.save_state()
        
    w.debugMode = not w.debugMode
    w.save_state()
    flash('Debug mode toggled.', 'info')
    return redirect(url_for('admin'))
    
@app.route('/save-block-multi', methods=['POST'])
def save_block_multi():
    print('saving on.......')
    data = request.get_json()
    file = data.get("file")
    print(file)
    for folder in w.folderDict.keys():
        if data.get('file') in w.folderDict[folder]:
            file = f"{folder}/" + file
            break

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
        w.save_state()
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
            w.save_state()
            return redirect(url_for('Home'))
        else:
            flash('Invalid credentials.', 'danger')
    
    w.currentPage = 'login.html'
    return render_template('login.html', all=w.__dict__, web=w)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'info')
    w.isLogedin = False
    w.save_state()
    return redirect(url_for('login'))

@app.route('/implement', methods=['GET'])
def implement_code():
    code = request.args.get('mainCode')
    w.write_code_to_page(w.previewPage,code,'element')
    flash('The Code implemented to the '+w.previewPage+' page', 'success')
    return redirect('admin')

@app.route('/favicon.ico')
def faviconn():
    return send_from_directory('static/favicon', 'logo.png')

#New Logic
@app.route('/<name>')
def render_page(name):
    if name == 'favicon.ico':
        return send_from_directory('static/favicon', 'logo.png')
        
    if name not in ["Home.html", "adminPanel.html"]:
        w.currentPage = name
        try:
            try:
                return render_template(f'Header_pages/{name}', all=w.__dict__, web = w)
            except:
                return render_template(f"partials/{name}", all=w.__dict__, web=w)
        except:
            return render_template(f"{name}", all=w.__dict__, web = w)
    else:
        print("dynamic-n")
        if name == "Home.html":
            return redirect(url_for('Home'))
        else:
            return redirect(url_for('admin'))
            
if __name__ == "__main__":
    app.run(debug=True)