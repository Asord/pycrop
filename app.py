from time import strftime, gmtime
from sys import argv
from pathlib import Path
from tkgen.gengui import TkJson
from PIL import ImageTk, Image

from utils import FFMPEG
from tools import pad, Vec2, RectToWHXY, vecPad

CANVAS_PADDING = Vec2(5, 5)

class Window(TkJson):
    def __init__(self, file, video_to_crop, title="Croppy", output_folder="", output_prefix="c_", tmp_folder="tmp"):
        with open(file, "r") as fs: gui = fs.read()
        TkJson.__init__(self, gui, title)

        self._video_to_crop = Path(video_to_crop).resolve()
        self._ffmpeg = FFMPEG(self._video_to_crop, output_folder=output_folder, output_prefix=output_prefix, tmp_folder=tmp_folder)
        self._length = self._ffmpeg.getLength()

        self._cPreview = self.get("cPreview")
        
        self._bGetPreview        = self.button("bGetPreview", cmd=self._getPreview)
        self._bCreatePreviewCrop = self.button("bCreatePreviewCrop", cmd=self._createPreviewCrop)

        self._bSave              = self.button("bSave", cmd=self._save)
        self._bCancel            = self.button("bCancel", cmd=self._cancel)

        self._lTimestamp = self.get("lTimestamp")
        self._sTimestamp = self.get("sTimestamp")
        self._sTimestamp.configure(command=self._onScaleChange)

        self._cPreview.bind("<Button-1>", self._startCropSelection)
        self._cPreview.bind("<B1-Motion>", self._moveCropSelection)

        self.update() # force winfo dimension to be updated
        
        self._previewImage = None

        self._canvasSize = Vec2(self._cPreview.winfo_width(), self._cPreview.winfo_height()) + 2*CANVAS_PADDING
        self._originalSize  = Vec2(0, 0)
        self._thumbnailSize = Vec2(0, 0)
        self._cropSelectionRect = [Vec2(0, 0), Vec2(0, 0)]
        self._cropSelection = None 

        self._onScaleChange(0)

    """ Utils """
    def ftime(self, time_percent):
        return strftime("%H:%M:%S", gmtime(self._length / 100 * int(time_percent)))

    def _scale(self):
        if self._previewImage is not None:
            # get WidthHeightXY from crop
            p1 = vecPad(self._cropSelectionRect[0], Vec2(5, 5), self._thumbnailSize)
            p2 = vecPad(self._cropSelectionRect[1], Vec2(5, 5), self._thumbnailSize)

            _WHXY = RectToWHXY(p1, p2)
            _WHXY[1] -= CANVAS_PADDING
            
            # pad out of bound values

            # translate to original size
            _thumbnailScale = self._originalSize.getScale(self._thumbnailSize)
            _WHXY[0] = _WHXY[0].scale(_thumbnailScale)
            _WHXY[1] = _WHXY[1].scale(_thumbnailScale)


            return *_WHXY[0].tuple(), *_WHXY[1].tuple()

    """ Scale """
    def _onScaleChange(self, value):
        self._lTimestamp.configure(text=self.ftime(value))
        self._ffmpeg.clearTmp()
        self._getPreview()


    """ Click & Drag """
    def _startCropSelection(self, evt):
        self._cropSelectionRect [0] = Vec2(evt.x, evt.y)

    def _drawSelectionRect(self):
        if self._cropSelection is not None: self._cPreview.delete(self._cropSelection) # delete already draw rect
        _rect = (*self._cropSelectionRect[0].tuple(), *self._cropSelectionRect[1].tuple())
        self._cropSelection = self._cPreview.create_rectangle(*_rect, outline="#f00", width=2)

    def _moveCropSelection(self, evt):
        self._cropSelectionRect[1] = Vec2(evt.x, evt.y)
        self._drawSelectionRect()


    """ Buttons """
    def _getPreview(self):
        ftime = self.ftime(self._sTimestamp.get())
        _tmp_file = self._ffmpeg.getScreenshot(ftime)

        # load image in canvas
        _image = Image.open(_tmp_file)
        self._originalSize = Vec2(*_image.size)

        _image.thumbnail(self._canvasSize.tuple(), Image.ANTIALIAS)
        self._thumbnailSize =  Vec2(*_image.size)

        # show preview image
        self._previewImage = ImageTk.PhotoImage(_image)
        self._cPreview.create_image(*CANVAS_PADDING.tuple(), image=self._previewImage, anchor='nw')
        
        self._drawSelectionRect()
        
    def _createPreviewCrop(self):
        if self._previewImage is not None:
            ftime = self.ftime(self._sTimestamp.get())
            self._ffmpeg.createPreviewCrop(self._scale(), ftime)
        
    def _save(self):
        if self._previewImage is not None:
            self._ffmpeg.crop(self._scale())

    def _cancel(self):
        exit(0)


if __name__ == "__main__":
    if len(argv) < 2:
        exit(-1)
    video_to_crop = argv[1]

    main = Window("gui.json", video_to_crop, output_folder="sample", output_prefix="crop_")
    main.mainloop()


