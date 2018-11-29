import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import os.path as path
import os
import sys
import shutil

import threading

PROGRAM_NAME = 'Archiver'
PROGRAM_PATH = path.abspath( path.dirname(sys.argv[0]) )
ICON_PATH = path.join(PROGRAM_PATH, 'icon', 'archiver.ico' )

AVAIABLE_FORMATS = [form for form, desc in shutil.get_archive_formats()]

STICK_TO_ALL = (tk.N, tk.S, tk.E, tk.W)
STICK_TO_SIDES = (tk.E, tk.W)
STICK_TO_TOP_BOTTOM = (tk.N, tk.S)

# Utility useless stuff

class LinkedNode:
	def __init__(self, value):
		self.val = value
		self.next = None
	
	def getVal(self):
		return self.val
	
	def getNext(self):
		return self.next

def makeLinkedNodes(*args):
	nodes = []
	for i, val in enumerate(args):
		nodes.append( LinkedNode(val) )
		if i > 0:
			nodes[i-1].next = nodes[i]
	
	return tuple(nodes)

class Switch:
	def __init__(self, firstNode, lastNode):
		lastNode.next = firstNode
		self.currentNode = firstNode
	
	def getCurrentVal(self):
		return self.currentNode.getVal()
	
	def switch(self):
		self.currentNode = self.currentNode.getNext()
		
		return self.getCurrentVal()

# Functions

def close_window():
	"""Close and exit"""
	mainWin.destroy()
	sys.exit(0)

def compressTarget():
	shutil.make_archive(path.splitext(currentOutpath.get())[0],
						currentAlgo.get(),
						root_dir = path.dirname( currentInputpath.get() ),
						base_dir = path.basename( currentInputpath.get() ) )
	
	progressBar.stop()

def compress():
	workThread = threading.Thread(target=compressTarget, daemon=False)
	
	progressBar.start(12)
	
	workThread.start()

def uncompressTarget():
	shutil.unpack_archive(currentInputpath.get(), extract_dir=currentOutpath.get())
	
	progressBar.stop()

def uncompress():
	workThread = threading.Thread(target=uncompressTarget, daemon=False)
	
	progressBar.start(12)
	
	workThread.start()

suffix_table = {
	'zip': 'zip',
	'tar': 'tar',
	'gztar': 'tar.gz',
	'bztar': 'tar.bz',
	'xztar': 'tar.xz'
}

def suffix(p, algo):
	return '{}.{}'.format( path.basename(p), suffix_table[algo] )

def switchPathLabels():
	inpathLabel.config( text=currentInpathLabel.switch() )
	outpathLabel.config( text=currentOutpathLabel.switch() )


def comprimirRadioAction():
	algoCombo.config(state='normal')
	switchPathLabels()
	
	inpathButton.config(command=selectInDir)
	outpathButton.config(command=selectOutFile)
	
	runButton.config(command=compress)

def descomprimirRadioAction():
	algoCombo.config(state='disabled')
	switchPathLabels()
	
	inpathButton.config(command=selectInFile)
	outpathButton.config(command=selectOutDir)
	
	runButton.config(command=uncompress)

def selectInDir():
	answer = filedialog.askdirectory(parent=mainWin, initialdir= os.getcwd(),
									 title='Seleccione el directorio a comprimir')
	
	if answer != '':
		currentInputpath.set(answer)
		currentOutpath.set( path.join( path.dirname(answer), suffix(answer, currentAlgo.get() )) )

def selectInFile():
	filetypes = [('todos', '.*')]
	for algo in AVAIABLE_FORMATS:
		filetypes.append( ( 'Archivo tipo {}'.format(algo), '.' + suffix_table[algo] ) )
	
	answer = filedialog.askopenfilename(parent=mainWin, initialdir=os.getcwd(),
										  initialfile=path.basename(currentInputpath.get()),
										  title='Seleccione archivo a abrir',
										  filetypes=filetypes)
	
	if answer != '':
		currentInputpath.set(answer)
		currentOutpath.set( path.splitext(answer)[0] )

def selectOutDir():
	
	answer = filedialog.askdirectory(parent=mainWin, initialdir=os.getcwd(),
									 title='Seleccione el directorio de salida')
	
	if answer != '':
		currentOutpath.set(answer)

def selectOutFile():
	filetypes = [('todos', '.*')]
	for algo in AVAIABLE_FORMATS:
		filetypes.append( ( 'Archivo tipo {}'.format(algo), '.' + suffix_table[algo] ) )
	
	answer = filedialog.asksaveasfilename(parent=mainWin, initialdir=os.getcwd(),
										  initialfile=path.basename(currentInputpath.get()),
										  title='Seleccione donde guardar',
										  defaultextension=suffix_table[currentAlgo.get()],
										  filetypes=filetypes)
	
	if answer != '':
		currentOutpath.set(answer)
	
# Main logic

if __name__ == '__main__':
	mainWin = tk.Tk()
	mainWin.title(PROGRAM_NAME)
	mainWin.iconbitmap(ICON_PATH)
	mainWin.columnconfigure(0, weight=1)
	mainWin.rowconfigure(0, weight=1)
	
	mainFrame = ttk.Frame(mainWin)
	mainFrame.grid(pady=12, padx=12, sticky=STICK_TO_ALL)
	mainFrame.columnconfigure(0, weight=1)
	mainFrame.columnconfigure(1, weight=1)
	mainFrame.rowconfigure(0, weight=1)
	mainFrame.rowconfigure(1, weight=1)
	mainFrame.rowconfigure(2, weight=1)
	
	
	modeFrame = ttk.LabelFrame(mainFrame, text='Modo')
	modeFrame.grid(column=0, row=0, sticky=STICK_TO_ALL)
	modeFrame.columnconfigure(0, weight=1)
	modeFrame.rowconfigure(0, weight=1)
	modeFrame.rowconfigure(1, weight=1)
	
	currentMode = tk.BooleanVar() # comprimir = 0, descomprimir = 1
	currentMode.set(0) # descomprimir es el default
	
	comprimirRadio = ttk.Radiobutton(modeFrame, text='Comprimir', variable=currentMode, value=0, command=comprimirRadioAction)
	comprimirRadio.grid(column=0, row=0)
	
	descomprimirRadio = ttk.Radiobutton(modeFrame, text='Descomprimir', variable=currentMode, value=1, command=descomprimirRadioAction)
	descomprimirRadio.grid(column=0, row=1)
	
	
	
	filenamesFrame = ttk.Frame(mainFrame)
	filenamesFrame.grid(column=1, row=0, sticky=STICK_TO_ALL, pady=12, padx=(6, 0) )
	filenamesFrame.columnconfigure(0, weight=0)
	filenamesFrame.columnconfigure(1, weight=2)
	filenamesFrame.columnconfigure(2, weight=2)
	filenamesFrame.rowconfigure(0, weight=1)
	filenamesFrame.rowconfigure(1, weight=1)
	
	
	currentInpathLabel = Switch( *makeLinkedNodes('Directorio de entrada', 'Archivo de entrada') )
	currentOutpathLabel = Switch( *makeLinkedNodes('Archivo de salida', 'Directorio de salida') )
	
	inpathLabel = ttk.Label(filenamesFrame, text=currentInpathLabel.getCurrentVal() )
	inpathLabel.grid(column=0, row=0, sticky=tk.E)
	
	outpathLabel = ttk.Label(filenamesFrame, text=currentOutpathLabel.getCurrentVal() )
	outpathLabel.grid(column=0, row=1, sticky=tk.E)
	
	currentInputpath = tk.StringVar()
	currentOutpath = tk.StringVar()
	
	inpathEntry = ttk.Entry(filenamesFrame, textvariable=currentInputpath)
	inpathEntry.grid(column=1, row=0, sticky=STICK_TO_SIDES)
	
	outpathEntry = ttk.Entry(filenamesFrame, textvariable=currentOutpath)
	outpathEntry.grid(column=1, row=1, sticky=STICK_TO_SIDES)
	
	inpathButton = ttk.Button(filenamesFrame, text='...', command=selectInDir)
	inpathButton.grid(column=2, row=0, sticky=STICK_TO_SIDES)
	
	outpathButton = ttk.Button(filenamesFrame, text='...', command=selectOutFile)
	outpathButton.grid(column=2, row=1, sticky=STICK_TO_SIDES)
	
	
	algoFrame = ttk.Frame(mainFrame)
	algoFrame.grid(column=0, row=1, sticky=STICK_TO_ALL, pady=(12, 0), padx=3)
	algoFrame.columnconfigure(0, weight=1)
	algoFrame.columnconfigure(1, weight=1)
	algoFrame.rowconfigure(0, weight=1)
	
	currentAlgo = tk.StringVar()
	if 'zip' in AVAIABLE_FORMATS:
		currentAlgo.set('zip')
	else:
		currentAlgo.set(AVAIABLE_FORMATS[0])
	
	algoCombo = ttk.Combobox(algoFrame, textvariable=currentAlgo, state='readonly')
	algoCombo['values'] = AVAIABLE_FORMATS
	algoCombo.pack()
	
	
	progressFrame = ttk.Frame(mainFrame)
	progressFrame.grid(column=1, row=1, sticky=STICK_TO_ALL)
	progressFrame.columnconfigure(0, weight=1)
	progressFrame.rowconfigure(0, weight=1)
	
	progressBar = ttk.Progressbar(progressFrame, orient='horizontal', mode='indeterminate')
	progressBar.grid(column=0, row=0, sticky=STICK_TO_SIDES, padx=40, pady=10)
	
	
	buttonsFrame = ttk.Frame(mainFrame)
	buttonsFrame.grid(column=1, row=2, sticky=STICK_TO_ALL, padx=(0, 10), pady=(10, 0) )
	buttonsFrame.columnconfigure(0, weight=2)
	buttonsFrame.columnconfigure(1, weight=0)
	buttonsFrame.rowconfigure(0, weight=1)
	
	runButton = ttk.Button(buttonsFrame, text='Correr', command=compress)
	runButton.grid(column=0, row=0, sticky=tk.E+tk.S)
	
	exitButton = ttk.Button(buttonsFrame, text='Salir', command=close_window)
	exitButton.grid(column=1, row=0, sticky=tk.W+tk.S)
	
	
	mainWin.mainloop()
