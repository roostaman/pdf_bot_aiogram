from PyPDF2 import PdfReader, PdfWriter
import os
import glob


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
    with open('results/result.pdf', 'wb') as of:
        writer.write(of)

    with open('results_back/result.pdf', 'wb') as of:
        writer.write(of)


def clear_directory(input_files):
    for file in input_files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")

    for file in glob.glob(os.path.join('results', '*')):
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")


input_files = glob.glob(os.path.join('files', '*.pdf'))

crop_and_merge(input_files)
clear_directory(input_files)
