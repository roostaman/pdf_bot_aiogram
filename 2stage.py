from PyPDF2 import PdfReader, PdfWriter
import zipfile
import os
import glob

zip_files = glob.glob(os.path.join('files', '*.zip'))


def unzip(zip_files):
    if not os.path.exists('files/extracted'):
        os.makedirs('files/extracted')

    if zip_files:
        for zip_file in zip_files:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall('files/extracted')
                zip_ref.close()

    return glob.glob(os.path.join('files/extracted', '*.pdf'))


# add page from reader, but crop it to 1/4 size:
def crop_page(page_to_crop):
    page = page_to_crop
    page.mediabox.lower_right = (
        page.mediabox.right / 2,
        page.mediabox.top / 2,
    )
    return page


# crop and merge pdfs:
def crop_and_merge(input_files):
    writer = PdfWriter()

    for file in input_files:
        with open(file, 'rb') as pdf_file:
            reader = PdfReader(pdf_file)

            for i in range(len(reader.pages)):
                page = reader.pages[i]
                cropped_page = crop_page(page_to_crop=page)
                writer.add_page(page=cropped_page)

    # write to output pdf file:
    with open('files/results/result.pdf', 'wb') as of:
        writer.write(of)

    with open('files/results_back/1.pdf', 'wb') as of:
        writer.write(of)


def clear_directory(input_files, zip_files):
    for file in input_files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")

    for file in glob.glob(os.path.join('files/results', '*')):
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")

    for file in zip_files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")


input_files = unzip(zip_files)
crop_and_merge(input_files)
clear_directory(input_files, zip_files)
