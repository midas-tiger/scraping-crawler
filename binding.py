"""
Contains methods for binding novel or manga into epub and mobi
"""
import io, os, random
from os import path
from subprocess import call
import json, base64
from ebooklib import epub
from PIL import Image


def epub_to_mobi(input_path):
    '''Converts epub file to mobi'''
    for file_name in sorted(os.listdir(input_path)):
        if not file_name.endswith('.epub'):
            continue
        input_file = path.join(input_path, file_name)
        kindlegen = path.join('lib', 'kindlegen', 'kindlegen')
        call([kindlegen, input_file])
    # end for
# end def

def novel_to_kindle(input_path):
    novel_id = path.basename(input_path)
    output_path = path.join('_book', novel_id)
    # Create epubs by volumes
    for volume_no in sorted(os.listdir(input_path)):
        # create book
        book = epub.EpubBook()
        book.set_identifier(novel_id + volume_no)
        book.set_language('en')
        book.add_author('Sudipto Chandra')
        # generate cover
        cover_file = random.choice(os.listdir('covers'))
        image = Image.open(path.join('covers', cover_file), mode='r')
        bytes_io = io.BytesIO()
        image.save(bytes_io, format='PNG')
        book.set_cover(file_name='cover.png', content=bytes_io.getvalue())
        # get chapters
        contents = []
        book_title = None
        vol = volume_no.rjust(2, '0')
        full_vol = path.join(input_path, volume_no)
        print('Processing:', full_vol)
        for file_name in sorted(os.listdir(full_vol)):
            # read data
            full_file = path.join(full_vol, file_name)
            item = json.load(open(full_file, 'r'))
            # add chapter
            xhtml_file = 'chap_%s.xhtml' % item['chapter_no'].rjust(4, '0')
            chapter = epub.EpubHtml(
                lang='en',
                file_name=xhtml_file,
                uid=item['chapter_no'],
                content=item['body'] or '',
                title=item['chapter_title'])
            book.add_item(chapter)
            contents.append(chapter)
            if not book_title:
                book_title = item['novel']
            # end if
        # end for
        book.spine = ['cover', 'nav'] + contents
        book.set_title(book_title + ' Volume ' + vol)
        book.toc = contents
        book.add_item(epub.EpubNav())
        book.add_item(epub.EpubNcx())
        # Create epub
        if not path.exists(output_path):
            os.makedirs(output_path)
        # end if
        file_name = novel_id + '_v' + volume_no + '.epub'
        file_path = path.join(output_path, file_name)
        print('Creating:', file_path)
        epub.write_epub(file_path, book, {})
    # end for
    # Convert to mobi format
    epub_to_mobi(output_path)
# end def

def manga_to_kindle(input_path):
    '''Convert crawled data to epub'''
    manga_id = path.basename(input_path)
    output_path = path.join('_book', manga_id)
    name = ' '.join([x.capitalize() for x in manga_id.split('_')])
    if not path.exists(output_path):
        os.makedirs(output_path)
    # end if
    call(['kcc-c2e',
          '-p', 'KPW',
          # '--forcecolor',
          # '-f', 'EPUB',
          '-t', name,
          '-o', output_path,
          input_path])
    # epub_to_mobi(output_path)
# end def
