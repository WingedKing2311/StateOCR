from preprocess import preprocess_image
from ocr_engine import run_ocr
from parser import structure_data
from display import display_table, save_csv

def main():
    image_path = "dataset/images/state_union_demo.png"

    processed_image = preprocess_image(image_path)

    extracted_text = run_ocr(processed_image)

    print("----- OCR TEXT START -----")
    print(extracted_text)
    print("----- OCR TEXT END -----")

    df = structure_data(extracted_text)

    display_table(df)
    save_csv(df, "output/transactions.csv")

if __name__ == "__main__":
    main()
