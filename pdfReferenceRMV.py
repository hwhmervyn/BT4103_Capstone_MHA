import argparse
import fitz
from pdfUtils import find_Reference, remove_reference
from customExceptions import CannotFindReference


def main(pdf_file_name, output_file):
    '''takes in a pdf file path and outputs a new pdf with reference removed. 
    Throws an exception if there is no reference detected'''
    try:
        doc = fitz.open(pdf_file_name)

        pgNo, _, reference_blks = find_Reference(doc)
        output_doc = fitz.open(pdf_file_name)
        output_doc = remove_reference(doc, output_doc, reference_blks, pgNo)

    except CannotFindReference as e:
        print(f"{e} -- output is just a copy of source")
        output_doc = doc

    output_doc.save(output_file)
    print(f'output saved to {output_file}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Takes in a pdf file and splits it into sections")
    parser.add_argument("--fp", type=str, help="source-file-path")
    parser.add_argument("--op", type=str, help="output-file-path")

    args = parser.parse_args()
    main(args.fp, args.op)
