import tkinter as tk
from tkinter import messagebox, Listbox
from tkcalendar import Calendar
import mysql.connector
from mysql.connector import Error
import datetime

# Janela principal
root = tk.Tk()
root.title("Agendador de Tarefas")
root.geometry("900x700")
root.configure(bg="#f2f2f2")

# Configuração do Banco de Dados (Para conectar tera que usar as imformações do Banco)
def conectar_bd():
    try:
        conexao = mysql.connector.connect(
            host='localhost',  # Substitua pelo seu host
            database='bd_calendario',
            user='root',       # Substitua pelo seu usuário MySQL
            password='sua_senha'  # Substitua pela sua senha MySQL
        )
        return conexao
    except Error as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")
        return None

# Funções de Cadastro e Login
def cadastrar_usuario():
    email = entrada_email.get()
    senha = entrada_senha.get()
    confirmacao = entrada_confirmacao.get()
    
    if not email or not senha or not confirmacao:
        messagebox.showwarning("Erro", "Todos os campos devem ser preenchidos.")
        return

    if senha != confirmacao:
        messagebox.showwarning("Erro", "As senhas não coincidem.")
        return

    conexao = conectar_bd()
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (email, senha) VALUES (%s, %s)", (email, senha))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            limpar_campos_cadastro()
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {e}")
        finally:
            cursor.close()
            conexao.close()

def login_usuario():
    email = entrada_email.get()
    senha = entrada_senha.get()
    
    conexao = conectar_bd()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
        usuario = cursor.fetchone()
        if usuario:
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            limpar_campos_cadastro()
            frame_login.pack_forget()
            frame_principal.pack()
        else:
            messagebox.showwarning("Erro", "Email ou senha incorretos.")
        cursor.close()
        conexao.close()

def limpar_campos_cadastro():
    entrada_email.delete(0, tk.END)
    entrada_senha.delete(0, tk.END)
    entrada_confirmacao.delete(0, tk.END)

# Funções de Tarefas
def adicionar_tarefa():
    tarefa = entrada_tarefa.get()
    data = calendario.get_date()

    if not tarefa:
        messagebox.showwarning("Erro", "Por favor, insira uma tarefa.")
        return

    # Converter a data para o formato YYYY-MM-DD
    data_formatada = datetime.datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")

    conexao = conectar_bd()
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute("INSERT INTO tarefas (data, tarefa, usuario_id) VALUES (%s, %s, %s)", 
                           (data_formatada, tarefa, 1))  # Substitua "1" pelo ID do usuário logado
            conexao.commit()
            atualizar_lista_tarefas()
            entrada_tarefa.delete(0, tk.END)
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao adicionar tarefa: {e}")
        finally:
            cursor.close()
            conexao.close()

def editar_tarefa():
    try:
        index = tarefas.curselection()[0]
        data, tarefa_atual = tarefas.get(index).split(": ")
        nova_tarefa = entrada_tarefa.get()

        if not nova_tarefa:
            messagebox.showwarning("Erro", "Por favor, insira a nova tarefa.")
            return

        conexao = conectar_bd()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("UPDATE tarefas SET tarefa = %s WHERE data = %s AND tarefa = %s AND usuario_id = %s",
                           (nova_tarefa, data, tarefa_atual, 1))  # Substitua "1" pelo ID do usuário logado
            conexao.commit()
            atualizar_lista_tarefas()
            entrada_tarefa.delete(0, tk.END)
            cursor.close()
            conexao.close()
    except IndexError:
        messagebox.showwarning("Erro", "Selecione uma tarefa para editar.")

def excluir_tarefa():
    try:
        index = tarefas.curselection()[0]
        data, tarefa = tarefas.get(index).split(": ")
        conexao = conectar_bd()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM tarefas WHERE data = %s AND tarefa = %s AND usuario_id = %s",
                           (data, tarefa, 1))  # Substitua "1" pelo ID do usuário logado
            conexao.commit()
            atualizar_lista_tarefas()
            cursor.close()
            conexao.close()
    except IndexError:
        messagebox.showwarning("Erro", "Selecione uma tarefa para excluir.")

def atualizar_lista_tarefas():
    tarefas.delete(0, tk.END)
    conexao = conectar_bd()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT data, tarefa FROM tarefas WHERE usuario_id = %s", (1,))  # Substitua "1"
        for data, tarefa in cursor.fetchall():
            tarefas.insert(tk.END, f"{data}: {tarefa}")
        cursor.close()
        conexao.close()

# Interface gráfica
# Frame de Cadastro/Login
frame_login = tk.Frame(root, bg="#f2f2f2", pady=10)
frame_login.pack(anchor="nw", padx=10, pady=10)

label_email = tk.Label(frame_login, text="Email:", bg="#f2f2f2")
label_email.pack(anchor="w")
entrada_email = tk.Entry(frame_login, width=30)
entrada_email.pack()

label_senha = tk.Label(frame_login, text="Senha:", bg="#f2f2f2")
label_senha.pack(anchor="w")
entrada_senha = tk.Entry(frame_login, show="*", width=30)
entrada_senha.pack()

label_confirmacao = tk.Label(frame_login, text="Confirme a Senha:", bg="#f2f2f2")
label_confirmacao.pack(anchor="w")
entrada_confirmacao = tk.Entry(frame_login, show="*", width=30)
entrada_confirmacao.pack()

botao_cadastrar = tk.Button(frame_login, text="Cadastrar", command=cadastrar_usuario, bg="#4CAF50", fg="white")
botao_cadastrar.pack(pady=5)

botao_login = tk.Button(frame_login, text="Login", command=login_usuario, bg="#2196F3", fg="white")
botao_login.pack()

# Frame Principal (escondido até o login)
frame_principal = tk.Frame(root, bg="#f2f2f2", pady=10)

# Frame de Cadastro de Tarefas
frame_cadastro = tk.Frame(frame_principal, bg="#f2f2f2", pady=10)
frame_cadastro.pack(anchor="nw", padx=10, pady=10)

label_tarefa = tk.Label(frame_cadastro, text="Tarefa:", bg="#f2f2f2")
label_tarefa.pack(side=tk.LEFT, padx=5)
entrada_tarefa = tk.Entry(frame_cadastro, width=40)
entrada_tarefa.pack(side=tk.LEFT, padx=5)

botao_adicionar = tk.Button(frame_cadastro, text="Adicionar", command=adicionar_tarefa, bg="#4CAF50", fg="white")
botao_adicionar.pack(side=tk.LEFT, padx=5)

botao_editar = tk.Button(frame_cadastro, text="Editar", command=editar_tarefa, bg="#FFA500", fg="white")
botao_editar.pack(side=tk.LEFT, padx=5)

botao_excluir = tk.Button(frame_cadastro, text="Excluir", command=excluir_tarefa, bg="#f44336", fg="white")
botao_excluir.pack(side=tk.LEFT, padx=5)

# Frame do calendário
frame_calendario = tk.Frame(frame_principal, bg="#f2f2f2", pady=10)
frame_calendario.pack(anchor="nw", padx=10, pady=10)

calendario = Calendar(frame_calendario, selectmode="day")
calendario.pack()

# Lista de tarefas
tarefas = Listbox(frame_principal, width=50, height=20)
tarefas.pack(padx=10, pady=10)

# Iniciar com o frame principal escondido
frame_principal.pack_forget()

root.mainloop()
