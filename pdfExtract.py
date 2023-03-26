import PyPDF4
import textract
import pytesseract
from PIL import Image
import io
import os
from wand.image import Image as wi
from fastapi import FastAPI, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()
# I used cors to allow all origins, as I was testing on localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# import fitz
# from io import BytesIO

# Works gr8 with StudentsList only, as gives row by row
# def extractText(file_path):
#     with open(file_path, "rb") as pdf_file:
#         pdf_reader = PyPDF4.PdfFileReader(pdf_file)
#         text = ""
#         for page_num in range(pdf_reader.getNumPages()):
#             page = pdf_reader.getPage(page_num)
#             text += page.extractText()
#     return text



# Works excellent with brochure, and also works with StudentsList (gives column by col)
def extractTextract(file_path):
    text = textract.process(file_path, method="pdfminer")
    text = text.decode("utf-8")
    print("Printing 1")
    return text

# trial function, not of use anymore
def extractTextFromImage(file_path):
    with Image.open(file_path) as img:
        recognized_text = pytesseract.image_to_string(img)
        print("Printing TextFrom Image")
        return recognized_text

# trial function, not of use anymore
def extractTextFromUnselectable(file_path):
    with open(file_path, "rb") as pdf_file:
        pdf_reader = PyPDF4.PdfFileReader(pdf_file)
        text = ""
        for page_num in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()
        if not text:
            for page_num in range(pdf_reader.getNumPages()):
                page = pdf_reader.getPage(page_num)
                image = page.getPixmap().getImage()
                # Save the image as a temporary file
                with open("temp_image.png", "wb") as temp_image:
                    temp_image.write(image)
                # Extract text from the image using Tesseract OCR
                recognized_text = extractTextFromImage("temp_image.png")
                # Append the recognized text to the text variable
                text += recognized_text
        # Return the extracted text as a string
        print("Printing from unslectable")
        return text


# Using wand, image_magick, works the bestttt with all types, but rarely gives error
def extractBest(pdf_path):
    try:
        pdfFile = wi(filename=pdf_path, resolution=120)
        image = pdfFile.convert("jpeg")
        print("This might take a few minutes")
        imageBlobs = []

        for img in image.sequence:
            imgPage = wi(image=img)
            imageBlobs.append(imgPage.make_blob("jpeg"))
        extract = []

        for imgBlob in imageBlobs:
            image = Image.open(io.BytesIO(imgBlob))
            text = pytesseract.image_to_string(image, lang="eng")
            extract.append(text)
        print("Printing from Best")
        return(extract)
    
    except:
        pdfFile = wi(filename=pdf_path)
        image = pdfFile.convert("jpeg")
        print("This might take a few minutes")

        imageBlobs = []

        for img in image.sequence:
            imgPage = wi(image=img)
            imageBlobs.append(imgPage.make_blob("jpeg"))
            print(imgPage)
        extract = []

        for imgBlob in imageBlobs:
            image = Image.open(io.BytesIO(imgBlob))
            text = pytesseract.image_to_string(image, lang="eng")
            extract.append(text)
        print("Printing from Best exception")
        return(extract)


#######################################
#######################################
def extractText(file_path):
    if (file_path.endswith(".pdf")):
        print('Processing with Basic Method...')
        text = extractTextract(file_path)
        print("Result: \n")
        if not text or text.strip()=='':
            print("Processing with Advanced Method...")
            text = extractBest(file_path)
            print("Result: \n")
            print("Printing from extractText1")
            return(text)
        else:
            print("Printing from extractText except")
            return(text)
    elif (file_path.endswith(".jpeg")) or file_path.endswith(".png") or file_path.endswith(".webp") or file_path.endswith(".jpg") or file_path.endswith(".tiff"):
        print("Processing Image to Text...")
        text = extractTextFromImage(file_path)
        print("Printing from extractText elif")
        return(text)
    else:
        print("Unsupported File Type")
        return("Unsupported File Type")

# print(extractText('single.pdf'))

@app.get("/")
def read_root():
    print("Hello World")
    return {"Hello": "World"}

@app.post("/uploadfile")
def upload_file(file: UploadFile = File(...)):
    print(file.filename)
    file_location = f"files/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    text = extractText(file_location)
    print(text)
    os.remove(file_location)
    # return {"filename": file.filename, "text": text}
    # json_comp = jsonable_encoder({
    #     "filename": file.filename,
    #     "text": text
    # })
    # return JSONResponse(content=json_comp)
    print("sending response")
    return {"filename": file.filename}


