import streamlit as st
import pandas as pd

# ==========================================
# 0. 簡易ログイン機能
# ==========================================
st.set_page_config(page_title="MicroAd Slide Generator", layout="wide")

def check_password():
    """パスワードが正しければTrueを返す関数"""
    def password_entered():
        # ▼▼ ここがパスワードです。好きなものに変更してください ▼▼
        if st.session_state["password"] == "microad2026":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # セキュリティのため保持を解除
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

# ==========================================
# ここから下は、パスワード正解時のみ実行・表示されます
# ==========================================
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
            border-bottom: 2px solid #ffb6c1; /* 少しピンクのアクセント */
            margin-bottom: 30px;
        }
        </style>
        <div class="brand-header">
            <h1 style="margin: 0; font-size: 28px;">🎯 MicroAd 提案スライド構成ジェネレーター</h1>
            <p style="margin: 5px 0 0 0; color: #555;">業種とデータアセットを選択し、NotebookLM用の最適な指示文を生成します。</p>
        </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # 2. 選択肢の定義
    # ==========================================
    INDUSTRIES = [
        "BtoB", "人材（採用）", "自治体", "学校", "小売り",
        "公営競技", "イベント", "ディーラー", "不動産", "流通", "金融"
    ]

    DATA_ASSETS = [
        "位置情報", "ワンキャリア", "APP起動データ",
        "シラレル（BtoB属性）", "年収", "マイクロアドデータ（4億UB）"
    ]

    # ==========================================
    # 3. ロジック：プロンプト生成
    # ==========================================
    def generate_prompt(uploaded_file, industry, selected_assets):
        try:
            xls = pd.ExcelFile(uploaded_file)
            data_text = ""
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                df = df.dropna(how='all').dropna(axis=1, how='all')
                data_text += f"\n### 【シート: {sheet_name}】\n"
                data_text += df.to_csv(index=False)
            
            asset_names = "、".join(selected_assets)
            
            prompt = f"""あなたはMicroAdの戦略立案責任者です。
今回、クライアントの業種【{industry}】向けに、以下の【活用データ】を用いた集客最大化プランの「スライド資料」を作成してください。

【対象業種】: {industry}
【今回活用するデータ】: {asset_names}
【デザインのトンマナ】: 白基調で、水色をメインカラー、アクセントに少量のピンクを使用した清潔感と信頼感のあるデザインを想定してください。

以下のシミュレーションデータを読み取り、選択されたMicroAd独自のデータの優位性を活かしたストーリーを組み立ててください。

### 指示事項：
1. スライド構成は「【{industry}】業界の課題」→「活用データ（{asset_names}）の解説」→「具体的なアプローチ」→「数値シミュレーション」の流れで作ること。
2. 添付データの「セグメント」「予算」「単価（CPC）」などを正確に引用し、シミュレーションスライドに反映すること。
3. 指定したトンマナ（白・水色・ピンク）に合うような、各スライドのビジュアルイメージ（配置する図解の提案など）もテキストで補足すること。

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
        st.subheader("1. 提案設定の入力")
        selected_industry = st.selectbox("📂 提案先の業種を選択してください", INDUSTRIES)
        selected_assets = st.multiselect(
            "📊 活用するデータを選択してください（複数選択可）",
            DATA_ASSETS,
            default=["マイクロアドデータ（4億UB）"]
        )
        up_file = st.file_uploader("📈 SIMファイル（Excel）をアップロード", type=["xlsx", "xls"])

    with col2:
        st.subheader("2. NotebookLM用 指示文")
        
        if up_file and selected_industry and selected_assets:
            with st.spinner("プロンプトを生成中..."):
                final_prompt = generate_prompt(up_file, selected_industry, selected_assets)
                
            st.success("✅ 生成完了！以下のテキストをコピーしてNotebookLMに貼り付けてください。")
            st.text_area("📋 コピー用テキスト", value=final_prompt, height=450)
            st.download_button(
                label="📄 テキストファイルとして保存",
                data=final_prompt,
                file_name=f"NotebookLM_Prompt_{selected_industry}.txt",
                mime="text/plain"
            )
        else:
            st.info("👈 左側のパネルで業種・データを選択し、Excelファイルをアップロードすると、ここに指示文が表示されます。")
