# AI-Recipe-Generator

基於自然語言生成技術，可根據使用者輸入的食材清單，動態生成專業食譜的 AI 引擎。

---

## 專案概述 (Overview)

`AI-Recipe-Generator` 是一個基於大型語言模型的條件式文本生成專案，專注於烹飪食譜領域。本專案旨在實現一個自動化流程：接收一組非結構化的食材列表作為輸入，並輸出一份包含標題、食材清單和詳細烹飪步驟的結構化、高品質食譜。

其核心是 `mbien/recipenlg` 模型，這是一個在 RecipeNLG 資料集上經過微調的 T5 (Text-to-Text Transfer Transformer) 模型，能夠理解食材與烹飪方法之間的複雜關係。

## 主要功能 (Features)

* **條件式文本生成 (Conditional Text Generation)**：根據使用者提供的食材條件動態生成文本。
* **支援結構化資料 (Structured Data Support)**：能夠解析輸入的食材列表，並生成包含特定標籤（如標題、步驟）的結構化食譜。
* **高品質自然語言輸出 (High-Quality Natural Language Output)**：生成的文本在語法、流暢度和連貫性上均表現出色。
* **模組化設計 (Modular Design)**：程式碼結構清晰，易於整合至其他應用程式或進行二次開發。

## 技術架構 (Technology Stack)

* **語言 (Language)**: Python 3.8+
* **核心函式庫 (Core Libraries)**:
    * Hugging Face Transformers
    * PyTorch
    * SentencePiece
* **底層模型 (Underlying Model)**: `mbien/recipenlg` (T5-base)
