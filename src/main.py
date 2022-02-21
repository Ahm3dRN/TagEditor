import sys
import time
import resources_rc
import eyed3
import webbrowser
from eyed3 import id3
from eyed3 import load
from PyQt5 import uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QEvent, QPoint
from ImageViewer import QImageViewer

repo = "https://github.com/Ahm3dRN/TagEditor"

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi("newui.ui", self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.installEventFilter(self)
        self.frame_8.installEventFilter(self)
        
        self.playlist_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.playlist_table.sortByColumn(1, Qt.AscendingOrder)
        self.playlist_table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.selectionModel = self.playlist_table.selectionModel()
        sizegrip = QtWidgets.QSizeGrip(self)
        sizegrip.setMinimumSize(8,8)
        sizegrip.setMaximumSize(8,8)
        self.horizontalLayout_2.addWidget(sizegrip)
        self.frame.hide()
        self.handle_buttons()
        self.current_tag = None
        self.current_a = None
        self.has_cover = False

    def handle_buttons(self):
        self.open_new_file.clicked.connect(self.add_song_to_list_update)
        self.save_metadata.clicked.connect(self.save_metadata_form)
        self.save_lyrics.clicked.connect(self.save_lyrics_form)
        self.sort_as.clicked.connect(self.sort_az)
        self.sort_ds.clicked.connect(self.sort_za)
        self.remove.clicked.connect(self.handle_table_remove)
        self.selectionModel.selectionChanged.connect(self.selChanged)
        self.cover_change.clicked.connect(self.handle_cover_change)
        self.cover_view.clicked.connect(self.handle_cover_view)
        self.cover_download.clicked.connect(self.handle_cover_download)
        self.cover_remove.clicked.connect(self.handle_cover_remove)
        self.minimize_button.clicked.connect(self.showMinimized)
        self.maxmize_button.clicked.connect(self.handle_maxmize)
        self.exit_button.clicked.connect(self.close)
        self.menu_button.clicked.connect(self.menuClicked)
        self.github.clicked.connect(self.open_repo)
    
    
    def open_repo(self):
        webbrowser.open(repo)

    def show_unloaded_warning(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("failed")
        msg.setInformativeText("Load audio first")
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def show_info(self, message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Info")
        msg.setInformativeText(message)
        msg.setWindowTitle("Info")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and obj.objectName() == "frame_8":
            self.oldPos = event.globalPos()
        elif event.type() == QEvent.MouseMove and obj.objectName() == "frame_8":
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
        return QtWidgets.QMainWindow.eventFilter(self, obj, event)

    def menuClicked(self):
        if self.frame.isHidden():
            self.frame.show()
        else:
            self.frame.hide()

    def handle_maxmize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def handle_table_remove(self):
        selected_items = self.selectionModel.selectedRows()
        for item in selected_items:
            self.playlist_table.removeRow(item.row())

    def handle_cover_remove(self):
        if not self.current_a:
            self.show_unloaded_warning()
            return
        
        imgs = self.current_a.tag.images
        try:
            image = imgs[-1]
            imgs.remove(image.description)
            self.current_a.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding='utf-8')
            self.set_default_cover()
            self.has_cover = False
        except IndexError:
            self.show_info("The Audio has no Cover")
            return
    
    def handle_cover_download(self):
        if not self.current_a:
            print("Load song first")
            self.show_unloaded_warning()
            return
        
        imgs = self.current_a.tag.images
        try:
            image = imgs[-1]
            itype = image.makeFileName("hi").split(".")[-1]
        except IndexError:
            self.show_info("The Audio has no Cover")
            return
        
        fileName , check = QFileDialog.getSaveFileName(None, "QFileDialog getSaveFileName() Demo",
                                                "", f"Image Files (*.{itype})") 
        if check:
            with open(fileName, "wb") as f:
                f.write(image.image_data)


    def handle_cover_view(self):
        if not self.current_a:
            print("Load song first")
            self.show_unloaded_warning()
            return
        
        
        if self.has_cover:
            imgs = self.current_a.tag.images
            print(type(imgs[0].image_data))
            self.imageViewer = QImageViewer(imgs[0].image_data)
            self.imageViewer.show()
        else:
            self.show_info("Audio has no cover")

    def handle_cover_change(self):
        if not self.current_a:
            self.show_unloaded_warning()
            return
        from eyed3.id3.frames import ImageFrame
        
        fileName = QFileDialog.getOpenFileName(self,
        "Open Image", ".", "Image Files (*.png *.jpg *.jpeg)")
        itype = fileName[0].split(".")[-1]
        if fileName[0] != "":
            ncover = open(fileName[0],'rb').read()
            self.current_a.tag.images.set(ImageFrame.FRONT_COVER, ncover, f'image/{itype}')
            self.current_a.tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION,encoding='utf-8')
            self.update_cover(ncover)
    
    def selChanged(self, a):
        if len(a.indexes()) > 0:
            it = self.playlist_table.item(a.indexes()[0].row(), 0)
            path = it.text()
            self.handle_new(path, source="selection")

    def sort_az(self):
        self.playlist_table.sortByColumn(1, Qt.AscendingOrder)

    def sort_za(self):
        self.playlist_table.sortByColumn(1, Qt.DescendingOrder)

    def save_lyrics_form(self):
        lyrics = self.lyrics_input.toPlainText()
        if self.current_tag:
            self.current_tag.lyrics.set(lyrics)
            self.current_tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding='utf-8')
            self.show_info("Saved")
        else:
            self.show_unloaded_warning()

    def save_metadata_form(self):
        # tag = id3.Tag()
        # tag.parse(self.file_path)
        # a = load(self.file_path)
        if not self.current_tag:
            self.show_unloaded_warning()
            return
        tag = self.current_tag
        a = self.current_a
        title = self.title_input.text()
        artist = self.artist_input.text()
        album = self.album_input.text()
        duration = self.duration_input.text()
        track = self.track_input.text()
        album_artist = self.album_artist_input.text()
        year = self.year_input.text()
        genre = self.genre_input.text()
        tag.artist = artist
        tag.album = album
        tag.title=title
        tag.album_artist = album_artist
        tag.track_num = int(track)
        tag.year = int(year)
        tag.genre = genre
        tag.save(version=eyed3.id3.ID3_DEFAULT_VERSION, encoding='utf-8')
        self.show_info("Saved")

    def add_entry(self, row: int, data: list):
        """
        Filename, Title, Artist, Album, track#, Year, Genre
            0       1       2       3       4       5     6
        """
        rows = self.playlist_table.rowCount()
        self.playlist_table.setRowCount(rows+1)
        self.file_path = data[0]
        for i, col in enumerate(data, start=0):
            item = QtWidgets.QTableWidgetItem(str(col))
            self.playlist_table.setItem(rows, i, item)


    def update_cover(self, image_data: bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.audio_cover.setScaledContents(True)
        self.audio_cover.setPixmap(pixmap)
        
    def set_default_cover(self):
        pixmap = QPixmap(":/panel/assets/default.jpg")
        self.audio_cover.setPixmap(pixmap)

    def add_song_to_list_update(self):
        fileName = QFileDialog.getOpenFileName(self,
        "Open Audio", ".", "Audio Files (*.mp3 *.wav *.ogg)")
        if fileName[0] != "":
            self.handle_new(fileName[0], source="open")
    
    def handle_new(self, path, source=""):
        tag = id3.Tag()
        tag.parse(path)
        a = load(path)
        if (a.tag == None):
            a.initTag()

        self.current_tag = tag
        self.current_a = a

        title = ""
        artist = ""
        album = ""
        duration = ""
        track = ""
        bit_rate = ""
        album_artist = ""
        best_date = ""
        year = ""
        genre = ""
        lyrics = ""
        if tag.title:
            title = tag.title
            self.set_title(title)
        imgs = a.tag.images
        if len(imgs) > 0:
            for image in a.tag.images:
                self.update_cover(image.image_data)
                self.has_cover = True
        else:
            self.set_default_cover()
            self.has_cover = False


        if tag.artist:
            artist = tag.artist
        
        if tag.album:
            album = tag.album
        
        if a.info.time_secs:
            duration = time.strftime("%H:%M:%S", time.gmtime(a.info.time_secs))
        
        if tag.track_num:
            track = f"{tag.track_num[0]}"
        
        if a.info.bit_rate:
            bit_rate = f"{a.info.bit_rate}, {a.info.bit_rate_str}"
        
        if tag.album_artist:
            album_artist = tag.album_artist
        
        if tag.getBestDate():
            year = f"{tag.getBestDate()}"

        if tag.genre:
            genre = tag.genre.name
        
        if tag.lyrics:
            lyrics = tag.lyrics[0].text

        self.set_artist(artist)
        self.set_album(album)
        self.duration_input.setText(duration)
        self.set_track(track)    
        self.bitrate_input.setText(bit_rate)
        self.album_artist_input.setText(album_artist)
        self.set_artist(artist)
        self.set_year(year)
        self.set_genre(genre)
        self.lyrics_input.setText(lyrics)
        self.access_date_input.setText(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tag.file_info.atime))}")
        self.modified_date_input.setText(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tag.file_info.mtime))}")
        
        if source == "open":
            self.add_entry(0, [path, title, artist, album, track, year, genre])
            


    def set_title(self, title):
        self.title_input.setText(title)
    
    def set_artist(self, artist):
        self.artist_input.setText(artist)

    def set_album(self, album):
        self.album_input.setText(album)

    def set_author(self, author):
        self.author_input.setText(author)

    def set_track(self, track):
        self.track_input.setText(track)

    def set_year(self, year):
        self.year_input.setText(year)

    def set_genre(self, genre):
        self.genre_input.setText(genre)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
    
if __name__ == '__main__':
    main()