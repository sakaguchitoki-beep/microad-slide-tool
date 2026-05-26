import streamlit as st
import pandas as pd

# ==========================================
# 0. 簡易ログイン機能
# ==========================================
st.set_page_config(page_title="MicroAd Slide Generator v3.2", layout="wide")

def check_password():
    def password_entered():
        if st.session_state["password"] == "microad2026":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 MicroAd Tool Login")
        st.info("このツールは社内専用です。共有パスワードを入力してください。")
        st.text_input("パスワード", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 MicroAd Tool Login")
        st.text_input("パスワード", type="password", on_change=password_entered, key="password")
        st.error("⚠️ パスワードが間違っています")
        return False
    return True

if check_password():

    # ==========================================
    # 1. UI設定・ブランドカラー適用
    # ==========================================
    st.markdown("""
        <style>
        .brand-header {
            background-color: #ffffff;
            color: #00a0e9;
            padding: 20px;
            border-radius: 8px;
            border-top: 5px solid #00a0e9;
            border-bottom: 2px solid #ffb6c1;
            margin-bottom: 30px;
        }
        </style>
        <div class="brand-header">
            <h1 style="margin: 0; font-size: 28px;">🎯 MicroAd 提案プロンプト生成（v3.2）</h1>
            <p style="margin: 5px 0 0 0; color: #555;">業種・配信手法・形式に合わせてNotebookLMへの指示文を最適化します。</p>
        </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # 2. 選択肢の定義
    # ==========================================
    INDUSTRIES = [
        "BtoB", "人材（採用）", "自治体", "学校", "小売り",
        "公営競技", "イベント", "ディーラー", "不動産", "流通", "金融", "サービス認知"
    ]

    DATA_ASSETS = [
        "位置情報", "ワンキャリア", "APP起動データ",
        "シラレル（BtoB属性）", "年収", "マイクロアドデータ（4億UB）", "購買データ"
    ]

    AD_METHODS = [
        "ディスプレイ（静止画）", "ディスプレイ（動画）", "Meta", "Youtube", "TVer"
    ]

    OUTPUT_FORMATS = ["提案資料用（複数スライド構成）", "ペライチ（1ページまとめ用）"]

    # ==========================================
    # 3. ロジック：プロンプト生成
    # ==========================================
    def generate_prompt(uploaded_file, industry, selected_assets, selected_methods, output_format):
        try:
            xls = pd.ExcelFile(uploaded_file)
            data_text = ""
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                df = df.dropna(how='all').dropna(axis=1, how='all')
                data_text += f"\n### 【シート: {sheet_name}】\n"
                data_text += df.to_csv(index=False)
            
            asset_names = "、".join(selected_assets)
            method_names = "、".join(selected_methods)
            
            # --- ペライチの指示を「絶対に1ページにするよう」強力に修正 ---
            if "ペライチ" in output_format:
                format_instruction = """
【超重要・厳守事項】
構成は「ペライチ（1ページ、またはスライド1枚のみ）」です。
絶対に複数ページ・複数スライドに分割しないでください。すべての情報を「1つの画面内に収まる文字数とレイアウト」で極限まで凝縮して出力してください。

以下の4要素を、箇条書きなどを活用して1ページ内にデザインしてください：
1. 【提案の核心】なぜこの施策をやるべきか（サマリー）
2. 【ターゲット】誰に当てるのか（データ選定理由）
3. 【配信手法】どう当てるのか（手法とシナリオ）
4. 【期待成果】いくらで何が得られるのか（SIMハイライト）
"""
            else:
                format_instruction = f"""
構成は「複数スライドの提案資料」として、以下の流れで詳細に作成してください：
1. 【{industry}】業界が今抱える課題と本施策の狙い
2. 活用データ（{asset_names}）の強みとターゲティングロジック
3. 配信手法（{method_names}）を組み合わせた具体的アプローチ
4. 配信シミュレーションの数値分析（正確な引用）
5. 来店計測やブランドリフト等の期待できる成果
"""

            prompt = f"""あなたはMicroAdの戦略立案責任者です。
クライアントの業種【{industry}】向けに、提案を作成してください。

【対象業種】: {industry}
【活用データ】: {asset_names}
【配信手法】: {method_names}
【デザインのトンマナ】: 白基調、メインカラー水色、アクセントにピンク。

{format_instruction}

### 配信手法に関する補足指示：
- 選択された「{method_names}」のそれぞれの特性（例：TVerならTVCMの補完、Youtubeなら態度変容、MetaならSNS親和性など）を考慮した解説を入れてください。

### 配信シミュレーションデータ (SIM):
{data_text}
"""
            return prompt
        except Exception as e:
            return f"エラーが発生しました: {e}"

    # ==========================================
    # 4. メイン画面レイアウト
    # ==========================================
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("1. 提案設定")
        selected_industry = st.selectbox("📂 提案先の業種", INDUSTRIES)
        selected_assets = st.multiselect("📊 活用データ", DATA_ASSETS, default=["マイクロアドデータ（4億UB）"])
        selected_methods = st.multiselect("📺 配信手法", AD_METHODS, default=["ディスプレイ（静止画）"])
        output_format = st.radio("📝 出力形式", OUTPUT_FORMATS)
        
        st.divider()
        up_file = st.file_uploader("📈 SIMファイル（Excel）をアップロード", type=["xlsx", "xls"])

    with col2:
        st.subheader("2. NotebookLM用 出力")
        
        if up_file and selected_industry and selected_assets and selected_methods:
            with st.spinner("最適化されたプロンプトを生成中..."):
                final_prompt = generate_prompt(up_file, selected_industry, selected_assets, selected_methods, output_format)
                
            st.success("✅ 生成完了！コピーしてNotebookLMへ。")
            st.text_area("📋 指示文", value=final_prompt, height=450)
            st.download_button(
                label="📄 保存する",
                data=final_prompt,
                file_name=f"NotebookLM_Prompt_{selected_industry}.txt",
                mime="text/plain"
            )
            
            st.divider()
            st.subheader("3. 仕上げ（提出用PDFの作成）")
            st.info("""
            NotebookLMで出力したPDFの右下には「NotebookLM」のロゴ透かしが入ります。
            クライアント提出用にロゴを消去したい場合は、以下の専用ツール（外部サイト）をご活用ください。
            """)
            st.markdown("👉 **[NotebookLM ロゴリムーバーを開く](https://notebooklmremover.com/ja)**")
            
        else:
            st.info("👈 設定を完了し、Excelをアップロードしてください。")
