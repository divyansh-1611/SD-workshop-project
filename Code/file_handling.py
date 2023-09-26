def printps(self):
    openfile = None
    ftypes = [('postscript files', '*.ps'), ('ALL files', '*')]
    openfile = asksaveasfilename(filetypes=ftypes)
    if openfile:
        outfile = os.path.abspath(openfile)
        self.ipostscript(outfile)


def ipostscript(self, file='drawing.ps'):
    ps = self.canvas.postscript()
    ps = ps.replace('1.000 1.000 1.000 setrgbcolor',
                    '0.000 0.000 0.000 setrgbcolor')
    fd = open(file, 'w')
    fd.write(ps)
    fd.close()


def fileopen(self):
    openfile = None
    ftypes = [('cadvas dwg', '*.pkl'), ('ALL FILES', '*')]
    openfile = askopenfilename(filetypes=ftypes, defaultextension='.pkl')
    if openfile:
        infile = os.path.abspath(openfile)
        self.load(infile)
        defaultextension


def fileImport(self):
    openfile = None
    ftypes = [('DXF format', '*.dxf'), ('ALL FIles', '*')]
    openfile = askopenfilename(filetypes=ftypes, defaultextension='.dxf')
    if openfile:
        infile = os.path.abspath(openfile)
        self.load(infile)


def filesave(self):
    openfile = self.filename
    if openfile:
        outfile = os.path.abspath(openfile)
        self.save(outfile)
    else:
        self.filesaveas()