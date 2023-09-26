import os
import pickle
from tkinter.filedialog import asksaveasfilename, askopenfilename
import dxf

class CADFileHandler:
    def __init__(self, initial_canvas=None, initial_filename=None, initial_curr=None):
        self.canvas = initial_canvas if initial_canvas is not None else None
        self.filename = initial_filename if initial_filename is not None else None
        self.curr = initial_curr if initial_curr is not None else {}

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

    def filesaveas(self):
        ftypes = [('CADvas dwg', '*.pkl'), ('ALL Files', '*')]
        openfile = asksaveasfilename(filetypes=ftypes, defaultextension='.pkl')
        if openfile:
            self.filename = openfile
            outfile = os.path.abspath(openfile)
            self.save(outfile)

    def save(self, file):
        drawlist = []
        for entity in self.curr.values():
            drawlist.append({entity.type: entity.get_attribs()})
        fext = os.path.splittext(file)[-1]
        if fext == '.dxf':
            import dxf
            dxf.native2dxf(drawlist, file)
        elif fext == '.pkl':
            with open(file, 'wb') as f:
                pickle.dump(drawlist, f)
                elf.filename = file
        elif not fext:
            print("Please type entire filename, including extension.")
        else:
            print("Save files of type {fext} not supported.")

    def load(self, file):
        """Load CAD data from file.
        Data is saved/loaded as a list of dicts, one dict for each
        drawing entity, {key=entity_type: val=entity_attribs} """
        
        # Determine the file extension (e.g., '.dxf' or '.pkl')
        fext = os.path.splitext(file)[-1]

        # Check the file extension to determine how to load the data
        if fext == '.dxf':
            drawlist = dxf.dxf2native(file) # Use 'dxf2native' function to convert DXF data
        elif fext == '.pkl':
            with open(file, 'rb') as f:
                drawlist = pickle.load(f)# Load data from a pickle file
            self.filename = file
        else:
            print("Load files of type {fext} not supported.")

         # Loop through the list of dictionaries containing entity data   
        for ent_dict in drawlist:
            # Extract the entity type (e.g., 'cl', 'cc', 'gl', etc.) from the dictionary
            if 'cl' in ent_dict:
                attribs = ent_dict['cl']
                e = entities.CL(attribs)
                self.cline_gen(e.coords)  # This method takes coords
            elif 'cc' in ent_dict:
                attribs = ent_dict['cc']
                e = entities.CC(attribs)
                self.cline_gen(e)
            elif 'gl' in ent_dict:
                attribs = ent_dict['gl']
                e = entities.GL(attribs)
                self.gline_gen(e)
            elif 'gc' in ent_dict:
                attribs = ent_dict['gc']
                e = entities.GC(attribs)
                self.gcirc_gen(e)
            elif 'ga' in ent_dict:
                attribs = ent_dict['ga']
                e = entities.GA(attribs)
                self.garc_gen(e)
            elif 'dl' in ent_dict:
                attribs = ent_dict['dl']
                e = entities.DL(attribs)
                self.dim_gen(e)
            elif 'tx' in ent_dict:
                attribs = ent_dict['tx']
                print(attribs)
                e = entities.TX(attribs)
                self.text_gen(e)
        self.view_fit()
        self.save_delta()  # undo/redo thing

    def close(self):
        self.quit()
