import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import subprocess
import keyword
import datetime

# メインウィンドウの作成
root = tk.Tk()
root.title("postblエディタ")
root.geometry("600x400")

# テキストボックスの作成
text_area = tk.Text(root, undo=True, wrap="word")
text_area.pack(expand=True, fill='both')

# キーワードや色の定義
keywords = keyword.kwlist
keyword_color = "blue"
string_color = "green"
comment_color = "gray"
text_color = "black"

# 作成履歴リスト
history = []

# シンタックスハイライト関数
def apply_syntax_highlighting(event=None):
    text = text_area.get(1.0, tk.END)

    # すべてのタグをクリア
    text_area.tag_remove("keyword", "1.0", tk.END)
    text_area.tag_remove("string", "1.0", tk.END)
    text_area.tag_remove("comment", "1.0", tk.END)

    # キーワードをハイライト
    for kw in keywords:
        start_idx = 1.0
        while True:
            start_idx = text_area.search(rf"\b{kw}\b", start_idx, tk.END, regexp=True)
            if not start_idx:
                break
            end_idx = f"{start_idx} + {len(kw)}c"
            text_area.tag_add("keyword", start_idx, end_idx)
            start_idx = end_idx

    # 文字列をハイライト
    start_idx = 1.0
    while True:
        start_idx = text_area.search(r'(\".*?\"|\'.*?\')', start_idx, tk.END, regexp=True)
        if not start_idx:
            break
        end_idx = f"{start_idx} + {len(text_area.get(start_idx, f'{start_idx} lineend'))}c"
        text_area.tag_add("string", start_idx, end_idx)
        start_idx = end_idx

    # コメントをハイライト
    start_idx = 1.0
    while True:
        start_idx = text_area.search(r'#.*', start_idx, tk.END, regexp=True)
        if not start_idx:
            break
        end_idx = f"{start_idx} lineend"
        text_area.tag_add("comment", start_idx, end_idx)
        start_idx = end_idx

# タグの設定
text_area.tag_config("keyword", foreground=keyword_color)
text_area.tag_config("string", foreground=string_color)
text_area.tag_config("comment", foreground=comment_color)

# キーバインディング
text_area.bind("<KeyRelease>", apply_syntax_highlighting)

# 履歴を追加する処理
def add_to_history(action_type, content):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append((timestamp, action_type, content))

# 新規作成の処理
def new_file():
    if messagebox.askokcancel("新規作成", "現在のファイルを保存しますか？"):
        save_file()
    text_area.delete(1.0, tk.END)
    root.title("無題 - postblエディタ")
    add_to_history("新規作成", text_area.get(1.0, tk.END))

# ファイル保存の処理
def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"),
                                                        ("Python files", "*.py"),
                                                        ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(text_area.get(1.0, tk.END))
        root.title(os.path.basename(file_path) + " - postblエディタ")
        messagebox.showinfo("保存", "ファイルが保存されました")
        add_to_history("ファイル保存", text_area.get(1.0, tk.END))

# 名前を付けて保存の処理
def save_as_file():
    save_file()

# 検索の処理
def find_text():
    search_term = simpledialog.askstring("検索", "検索するテキスト:")
    if search_term:
        start_pos = text_area.search(search_term, "1.0", tk.END)
        if start_pos:
            end_pos = f"{start_pos}+{len(search_term)}c"
            text_area.tag_add("highlight", start_pos, end_pos)
            text_area.tag_config("highlight", background="yellow", foreground="black")
            text_area.mark_set("insert", end_pos)
            text_area.see("insert")
        else:
            messagebox.showinfo("検索", "テキストが見つかりませんでした")

# 置換の処理
def replace_text():
    search_term = simpledialog.askstring("置換", "置換するテキスト:")
    if search_term:
        replace_term = simpledialog.askstring("置換", "新しいテキスト:")
        start_pos = text_area.search(search_term, "1.0", tk.END)
        if start_pos and replace_term:
            end_idx = f"{start_pos}+{len(search_term)}c"
            text_area.delete(start_pos, end_idx)
            text_area.insert(start_pos, replace_term)
            text_area.tag_remove("highlight", "1.0", tk.END)
            text_area.mark_set("insert", f"{start_pos}+{len(replace_term)}c")
            text_area.see("insert")
            add_to_history("置換", text_area.get(1.0, tk.END))

# 全て置換の処理
def replace_all():
    search_term = simpledialog.askstring("全て置換", "置換するテキスト:")
    if search_term:
        replace_term = simpledialog.askstring("全て置換", "新しいテキスト:")
        pos = "1.0"
        while True:
            start_pos = text_area.search(search_term, pos, tk.END)
            if not start_pos:
                break
            end_idx = f"{start_pos}+{len(search_term)}c"
            text_area.delete(start_pos, end_idx)
            text_area.insert(start_pos, replace_term)
            pos = f"{start_pos}+{len(replace_term)}c"
        text_area.tag_remove("highlight", "1.0", tk.END)
        messagebox.showinfo("全て置換", "全ての置換が完了しました")
        add_to_history("全て置換", text_area.get(1.0, tk.END))

# 元に戻すの処理
def undo_action():
    try:
        text_area.edit_undo()
        add_to_history("元に戻す", text_area.get(1.0, tk.END))
    except tk.TclError:
        pass

# やり直し（1つ進む）の処理
def redo_action():
    try:
        text_area.edit_redo()
        add_to_history("やり直し", text_area.get(1.0, tk.END))
    except tk.TclError:
        pass

# 全て選択の処理
def select_all():
    text_area.tag_add("sel", "1.0", "end")

# 部分選択の処理
def select_part():
    start_idx = simpledialog.askstring("部分選択", "開始位置 (例: 1.0):")
    end_idx = simpledialog.askstring("部分選択", "終了位置 (例: 2.0):")
    if start_idx and end_idx:
        try:
            text_area.tag_add("sel", start_idx, end_idx)
        except tk.TclError:
            messagebox.showerror("エラー", "指定された範囲を選択できませんでした。")

# コピーの処理
def copy_text():
    text_area.event_generate("<<Copy>>")

# 全削除の処理
def delete_all():
    text_area.delete("1.0", tk.END)
    add_to_history("全削除", "")

# 貼り付けの処理
def paste_text():
    text_area.event_generate("<<Paste>>")
    add_to_history("貼り付け", text_area.get(1.0, tk.END))

# PIPインストール履歴の表示
def show_pip_history():
    try:
        result = subprocess.run(["pip", "list", "--format=columns"], stdout=subprocess.PIPE, text=True)
        installed_packages = result.stdout
        if installed_packages:
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, installed_packages)
            apply_syntax_highlighting()
            messagebox.showinfo("PIP履歴", "PIPインストール履歴が表示されました")
        else:
            messagebox.showinfo("PIP履歴", "インストール済みパッケージはありません")
    except Exception as e:
       messagebox.showerror("エラー", f"PIP履歴の取得中にエラーが発生しました:\n{e}")

# インストールされているプログラミング言語の確認
def check_installed_languages():
    languages = {
        "Python": ["python", "--version"],
        "Java": ["java", "-version"],
        "Node.js": ["node", "--version"],
        "Ruby": ["ruby", "--version"],
        "Perl": ["perl", "-v"],
        "Go": ["go", "version"],
        "PHP": ["php", "--version"],
        "Rust": ["rustc", "--version"],
    }

    installed_languages = []
    for lang, command in languages.items():
        try:
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            installed_languages.append(lang)
        except FileNotFoundError:
            continue

    if installed_languages:
        languages_list = "\n".join(installed_languages)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "Installed Programming Languages:\n\n" + languages_list)
        apply_syntax_highlighting()
        messagebox.showinfo("言語確認", "インストールされているプログラミング言語が表示されました")
    else:
        messagebox.showinfo("言語確認", "インストールされているプログラミング言語が見つかりませんでした")

# 履歴表示の処理
def show_history():
    if history:
        history_list = "\n".join([f"{i+1}. [{timestamp}] {action_type}" for i, (timestamp, action_type, _) in enumerate(history)])
        selected_index = simpledialog.askinteger("作成履歴", f"履歴を選択:\n{history_list}\n\n選択番号:")
        if selected_index and 1 <= selected_index <= len(history):
            selected_history = history[selected_index - 1]
            return selected_history
        else:
            messagebox.showerror("エラー", "有効な履歴番号を選択してください。")
            return None
    else:
        messagebox.showinfo("履歴", "作成履歴はありません。")
        return None

# 履歴からテキストを復元する処理
def restore_from_history():
    selected_history = show_history()
    if selected_history:
        _, _, content = selected_history
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, content)
        apply_syntax_highlighting()
        messagebox.showinfo("復元", "選択された履歴からテキストが復元されました。")

# PIPパッケージをインストールする処理
def install_package():
    package_name = simpledialog.askstring("PIPインストール", "インストールするパッケージ名を入力:")
    if package_name:
        try:
            result = subprocess.run(["pip", "install", package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout + result.stderr
            if "Successfully installed" in output:
                messagebox.showinfo("PIPインストール", f"{package_name} が正常にインストールされました。")
            else:
                messagebox.showwarning("PIPインストール", f"{package_name} のインストールに失敗しました。\n{output}")
        except Exception as e:
            messagebox.showerror("エラー", f"PIPインストール中にエラーが発生しました:\n{e}")
    else:
        messagebox.showinfo("PIPインストール", "パッケージ名が入力されませんでした。")

# PIPパッケージをアンインストールする処理
def uninstall_package():
    try:
        result = subprocess.run(["pip", "list", "--format=columns"], stdout=subprocess.PIPE, text=True)
        installed_packages = result.stdout
        if installed_packages:
            packages = [line.split()[0] for line in installed_packages.splitlines()[2:]]
            package_name = simpledialog.askstring("PIPアンインストール", f"アンインストールするパッケージを選択:\n{', '.join(packages)}")
            if package_name in packages:
                confirm = messagebox.askyesno("確認", f"{package_name} をアンインストールしてもよろしいですか？")
                if confirm:
                    result = subprocess.run(["pip", "uninstall", package_name, "-y"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    output = result.stdout + result.stderr
                    if "Successfully uninstalled" in output:
                        messagebox.showinfo("PIPアンインストール", f"{package_name} が正常にアンインストールされました。")
                    else:
                        messagebox.showwarning("PIPアンインストール", f"{package_name} のアンインストールに失敗しました。\n{output}")
            else:
                messagebox.showerror("エラー", "無効なパッケージ名が選択されました。")
        else:
            messagebox.showinfo("PIPアンインストール", "インストール済みパッケージはありません。")
    except Exception as e:
        messagebox.showerror("エラー", f"PIPアンインストール中にエラーが発生しました:\n{e}")

# メニューバーの作成
menu_bar = tk.Menu(root)

# ファイルメニューの作成
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="新規作成", command=new_file)
file_menu.add_command(label="保存", command=save_file)
file_menu.add_command(label="名前を付けて保存", command=save_as_file)
file_menu.add_separator()
file_menu.add_command(label="終了", command=root.quit)
menu_bar.add_cascade(label="ファイル", menu=file_menu)

# 編集メニューの作成
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="元に戻す", command=undo_action)
edit_menu.add_command(label="やり直し", command=redo_action)
edit_menu.add_separator()
edit_menu.add_command(label="全て選択", command=select_all)
edit_menu.add_command(label="部分選択", command=select_part)
edit_menu.add_command(label="コピー", command=copy_text)
edit_menu.add_command(label="全削除", command=delete_all)
edit_menu.add_command(label="貼り付け", command=paste_text)
edit_menu.add_separator()
edit_menu.add_command(label="検索", command=find_text)
edit_menu.add_command(label="置換", command=replace_text)
edit_menu.add_command(label="全て置換", command=replace_all)
menu_bar.add_cascade(label="編集", menu=edit_menu)

# ツールメニューの作成
tools_menu = tk.Menu(menu_bar, tearoff=0)
tools_menu.add_command(label="PIPインストール履歴", command=show_pip_history)
tools_menu.add_command(label="インストールされているプログラミング言語", command=check_installed_languages)
tools_menu.add_command(label="作成履歴の表示", command=show_history)
tools_menu.add_command(label="履歴から復元", command=restore_from_history)
tools_menu.add_command(label="PIPパッケージインストール", command=install_package)
tools_menu.add_command(label="PIPパッケージアンインストール", command=uninstall_package)
menu_bar.add_cascade(label="ツール", menu=tools_menu)

# メニューバーの設定
root.config(menu=menu_bar)

# イベントループの開始
root.mainloop()