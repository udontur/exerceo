# Local
import Sysenv

# Utilities
import os
import base64


async def promptResponse(prompt, llmModel, llmClient):
    response = await llmClient.chat.completions.create(
        model=os.getenv(llmModel),
        messages=prompt,
    )
    return response.choices[0].message.content


async def rawLatexToParsedLatex(rawLatex):
    questionExtractionPrompt = """
    **Objective**: Extract and structure individual questions from practice/exam papers while preserving original formatting and grouping related multi-part questions.

    **Input Processing Rules**:
    - Extract ONLY question text and associated sub-questions.
    - Remove: Instructions, headings, page numbers, section titles, author information, copyright notices, and other contextual metadata.
    - Preserve mathematical expressions, LaTeX formatting, and special symbols exactly as written.
    - Treat sub-questions (e.g. part a and part b) as the same question as the main question.

    **Output Rules**:
    - Separate each complete question (including all sub-parts) with exactly two newline characters (`\n\n`).

    **Input Text to Parse**:
    """
    print("DEEPSEEk")
    prompt = [
        {"role": "system", "content": questionExtractionPrompt},
        {"role": "user", "content": rawLatex},
    ]
    return await promptResponse(
        prompt=prompt,
        llmModel="LLM_MODEL",
        llmClient=Sysenv.genericLLMClient,
    )


# TODO: replace with deepseek-ocr when it is available on platforms.deepseek.com
async def imageToLatex(imageBytes):
    imageBase64 = base64.b64encode(imageBytes).decode()
    prompt = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extract all text and tables in LaTeX format.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{imageBase64}"},
                },
            ],
        }
    ]    
    print("clarifai")
    return await promptResponse(
        prompt=prompt,
        llmModel="OCR_MODEL",
        llmClient=Sysenv.ocrLLMClient,
    )
