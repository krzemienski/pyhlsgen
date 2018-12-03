import os
import sys
import subprocess
from info.movie import Source
from info.movie import Manager


def main():
    manager = Manager()
    manager.make_directory(path=Source.DESTINATION_FILE_DIRECTORY.value)
    working_directory = os.path.join(Source.SOURCE_FILE_DIRECTORY.value, Source.DESTINATION_FILE_DIRECTORY.value)

    for f in manager.get_movie_list():
        replace_file_name = manager.get_replace_character(name=f)
        try:
            os.rename(f, replace_file_name)
        except OSError as e:
            print(f'RENAME中にエラーが発生しました...\n対象ファイル: {f}\nエラー内容: {e}')
        else:
            vcodec = 'libx265'
            acodec = 'copy'
            target_dir = os.path.join(working_directory, f.replace(' ', '_'))

            if not os.path.exists(target_dir):
                manager.make_directory(path=target_dir)
                comm = f"ffmpeg -i {os.path.join(working_directory, replace_file_name)}" \
                    f"-max_muxing_queue_size 1024 -c:v {vcodec} -tag:v hvc1 -vbsf hevc_mp4toannexb "\
                    f"-c:a {acodec} -ar 44100 -pix_fmt yuv420p -map 0:0 -map 0:1 "\
                    f"-f segment -segment_format mpegts -segment_time 10 "\
                    f"-segment_list {os.path.join(target_dir, 'output.m3u8')} " \
                    f"{os.path.join(target_dir, 'stream-%06d.ts')}"
                comm = comm.split(" ")

                if Source.PLATFORM.value == 'win32':
                    subprocess.run(['chcp', '65001'], shell=True, encoding='utf-8')
                    subprocess.run(comm, shell=True, encoding='utf-8')
                elif Source.PLATFORM.value == 'linux':
                    subprocess.run(comm, shell=False, encoding='utf-8')
                else:
                    print('対応していないディストリビューションで実行しています...\nプログラムを終了します。')
                    sys.exit(1)
            else:
                print(f'{f}は既にありますのでスキップします...')

        finally:
            os.rename(replace_file_name,  f)
            print(f"処理が終わったので、元のファイル名にRENAME完了...{os.path.join(working_directory, f)}")


main()
if Source.PLATFORM.value == 'win32':
    input("\n\nすべての処理が完了しました...")
