# https://pypi.org/project/pytubefix/
# https://github.com/JuanBindez/pytubefix
# pytube가 제대로 동작을 안하므로 해당 라이브러리 사용

from pytubefix import YouTube # pip install pytubefix
import os
from PyQt5 import QtWidgets, QtCore # pip install pytube PyQt5

class YoutubeDownloaderApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # 윈도우 설정
        self.setWindowTitle('YouTube Downloader')
        self.setGeometry(300, 300, 400, 200)

        # 위젯 설정
        self.url_label = QtWidgets.QLabel("YouTube URL:")
        self.url_input = QtWidgets.QLineEdit(self)
        
        self.video_radio = QtWidgets.QRadioButton("Video")
        self.video_radio.setChecked(True)
        self.audio_radio = QtWidgets.QRadioButton("Audio (MP3)")
        
        self.download_button = QtWidgets.QPushButton("Download")
        self.status_label = QtWidgets.QLabel("Status: Waiting")
        
        # 레이아웃 설정
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.video_radio)
        layout.addWidget(self.audio_radio)
        layout.addWidget(self.download_button)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 신호 연결
        self.download_button.clicked.connect(self.download_video)
    
    def download_video(self):
        url = self.url_input.text()
        if not url:
            self.status_label.setText("Status: Please enter a URL")
            return

        # UI 비활성화
        self.disable_ui()

        try:
            yt = YouTube(url)
            title = yt.title
            self.status_label.setText(f"Status: Downloading {title}...")
            QtCore.QCoreApplication.processEvents()  # UI 업데이트
            
            save_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Download Directory')
            if not save_path:
                self.status_label.setText("Status: Download cancelled")
                return
            
            if self.video_radio.isChecked():
                stream = yt.streams.get_highest_resolution()  # 고화질 비디오 선택
                output_file = stream.download(output_path=save_path)
            else:
                stream = yt.streams.filter(only_audio=True).first()  # 오디오만 선택
                output_file = stream.download(output_path=save_path)
                base, ext = os.path.splitext(output_file)
                new_file = base + '.mp3'
                os.rename(output_file, new_file)
                output_file = new_file  # MP3 파일로 업데이트

            # 중복 파일 이름 처리
            unique_file = self.get_unique_filename(save_path, title, ".mp4" if self.video_radio.isChecked() else ".mp3")
            os.rename(output_file, os.path.join(save_path, unique_file))
            
            self.status_label.setText(f"Status: {unique_file} downloaded successfully")
        
        except Exception as e:
            self.status_label.setText(f"Status: Error - {str(e)}")
        
        # UI 재활성화
        self.enable_ui()

    def disable_ui(self):
        """Disable the UI elements during the download process."""
        self.url_input.setDisabled(True)
        self.video_radio.setDisabled(True)
        self.audio_radio.setDisabled(True)
        self.download_button.setDisabled(True)

    def enable_ui(self):
        """Enable the UI elements after the download process is complete."""
        self.url_input.setDisabled(False)
        self.video_radio.setDisabled(False)
        self.audio_radio.setDisabled(False)
        self.download_button.setDisabled(False)

    def get_unique_filename(self, path, title, extension):
        """중복 파일 이름을 피하기 위해 고유한 파일 이름을 생성합니다."""
        base_filename = title.strip().replace(" ", "_")  # 공백을 '_'로 치환
        filename = base_filename + extension
        full_path = os.path.join(path, filename)
        counter = 1
        
        # 파일이 존재할 경우, 파일명 뒤에 숫자를 붙임
        while os.path.exists(full_path):
            filename = f"{base_filename}_{counter}{extension}"
            full_path = os.path.join(path, filename)
            counter += 1
            
        return filename

# PyQt5 앱 실행
app = QtWidgets.QApplication([])
window = YoutubeDownloaderApp()
window.show()
app.exec_()
