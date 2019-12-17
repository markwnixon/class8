from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from PyPDF2.pdf import PageObject
from CCC_system_setup import addpath, addpath2, addtxt, scac


def blendticks(gfile1,gfile2,outfile):

    reader1 = PdfFileReader(open(gfile1, 'rb'))
    p1 = reader1.getPage(0)

    reader2 = PdfFileReader(open(gfile2, 'rb'))
    p2 = reader2.getPage(0)
    #p2.cropBox.lowerLeft = (50,400)
    #p2.cropBox.upperRight = (600,700)

    #offset_x = p2.mediaBox[2]
    offset_x = 0
    offset_y = -280

    # add second page to first one
    p1.mergeTranslatedPage(p2, offset_x, offset_y, expand=False)
    p1.cropBox.lowerLeft = (50,250)
    p1.cropBox.upperRight = (550,800)

    output = PdfFileWriter()
    output.addPage(p1)

    with open(outfile, "wb") as out_f:
        output.write(out_f)
