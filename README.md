## OCR Data Generator

The OCR Data Generator is a model designed to generate synthetic data with OCR (Optical Character Recognition) capabilities. It supports a wide range of fonts and backgrounds for generating diverse datasets. The current features of the model are as follows:

- **Saving Text Detection Data**: The model can save text detection data in the form of straight rectangles, which can be easily read using the labelme tool.
- **Finding Suitable Background Positions**: It utilizes OpenCV's imageIntegral to find appropriate positions in the image for placing the generated text, considering the background context.
- **Color Generation**: The model generates text colors that ensure the text remains distinct from the background color.

### Model Drawbacks

While the OCR Data Generator offers valuable functionality, it has a few limitations:

- **Slow Image Generation Speed**: The speed of image generation can be relatively slow, depending on the specified parameters.
- **Unsuitable Background Placement**: In some cases, the model may struggle to find a suitable area to place the generated text on certain background images.
- **Unlabeled Pre-existing Text**: If the background image already contains texts, the model does not label these texts in the generated image.

### Instructions for Use

To use the OCR Data Generator, follow these steps:

1. **Install the Package**: Execute the following command to install the required dependencies:
    ```shell
    pip install -r requirements.txt
    ```

2. **Set up Parameters**: Adjust the necessary parameters, input directory, and output directory within the `main.py` file to customize the data generation process.

3. **Run Data Generation**: Execute the following command to start generating the synthetic data:
    ```shell
    python main.py
    ```
