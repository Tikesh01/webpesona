from flask import Flask, render_template, request,redirect, url_for
import os
import shutil

app = Flask(__name__)

class website:
    def __init__(self):
        self.size = "100%"
        self.admin = "templates/adminPanel.html"
        self.folder = "templates/"
        self.extantion = ".html"
        self.pages = [page for page in os.listdir('templates/') if not os.path.isdir('templates/'+page) ]
        self.folders =  [page for page in os.listdir('templates/') if os.path.isdir('templates/'+page) ]
        self.folderDict = {folder : os.listdir("templates/"+folder) for folder in self.folders}
        self.favicons = os.listdir("static/favicons/")
        self.favicon = os.listdir("static/favicon/")
        self.pages.remove('adminPanel.html')
        self.previewPage = "/"
        self.logo = os.listdir("static/logo/")
        self.contentEditable = False
        self.currentPage="home.html"
        self.themes = self.theme()

    def theme(self):
        file = open("static/root.css", "r")
        return file.readlines()
            
    def changeTheme(self, direction):
        with open("static/root.css", "r") as file:
            lines = file.readlines()

        # Only rotate if enough lines
        if len(lines) >= 15:
            if direction == 'right':
                first15 = lines[:15]
                remaining = lines[15:]
                newLines = remaining + first15
            elif direction == 'left':
                last15 = lines[-15:]
                remaining = lines[:-15]
                newLines = last15 + remaining

            with open("static/root.css", "w") as file:
                file.writelines(newLines)
        
        self.themes = self.theme()
        return redirect('/admin')
    

    def addPage(self, name):  
        # Create the page file if it doesn't exist
        file_path = self.folder + name + self.extantion
        if not os.path.exists(file_path):
            with open("templates/partials/skeleton.html", "r") as skeleton:
                with open(file_path, "w") as file:
                    file.write(skeleton.read())        
        self.pages = [page for page in os.listdir('templates/') if not os.path.isdir('templates/'+page) ]
        self.pages.remove('adminPanel.html')
        
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
        self.size = FrameSize
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
        
w =website()
        
@app.route('/')
def interface():
    print(w.currentPage)
    w.contentEditable = False
    w.currentPage = "home.html"
    return render_template('home' + w.extantion, all=w.__dict__)

@app.route('/admin')
def admin():
    w.currentPage = "adminPanel.html"
    w.contentEditable = True
    print(w.currentPage)
    return render_template("adminPanel.html",  all=w.__dict__)
        
        
@app.route('/pageAddition', methods=['POST'])
def fuc():
    name = request.form.get("fileName")
    w.addPage(name=name)
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
        print(w.previewPage)
        w.previewPage = pathForPreview
        print(w.previewPage)
    
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

@app.route('/<name>')
def render_page(name):
    if name != "home.html" or name !="adminPanel.html" :
        w.currentPage = name 
        return render_template(f"{name}", all=w.__dict__)
    else:
        if name=="home.html":
            redirect(url_for(''))
        else:
            redirect(url_for('admin'))
            

if __name__ == "__main__":
    app.run(debug=True)
    
    
