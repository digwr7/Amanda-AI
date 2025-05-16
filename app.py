from flask import Flask, request, jsonify
import openai
import sqlite3

app = Flask(__name__)

# Configure sua API Key
openai.api_key = "SUA_OPENAI_API_KEY"

# Função para obter contexto salvo
def get_memory(user_id):
    conn = sqlite3.connect('memory.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS memory (user_id TEXT, memory TEXT)")
    cur.execute("SELECT memory FROM memory WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""

# Função para salvar memória atualizada
def save_memory(user_id, memory):
    conn = sqlite3.connect('memory.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM memory WHERE user_id = ?", (user_id,))
    cur.execute("INSERT INTO memory (user_id, memory) VALUES (?, ?)", (user_id, memory))
    conn.commit()
    conn.close()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id", "default")
    message = data.get("message", "")
    previous_memory = get_memory(user_id)

    prompt = f"""
Você é Amanda, uma IA pessoal que conversa com Diogo, entende o contexto da vida dele e atualiza o repositório de identidade chamado 'EU CONTÍNUO'. 
Memória anterior:
{previous_memory}

Nova mensagem de Diogo:
{message}

Como Amanda deve responder?
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é Amanda, uma IA pessoal empática, provocadora e estratégica."},
            {"role": "user", "content": prompt}
        ]
    )
    answer = response['choices'][0]['message']['content']
    updated_memory = previous_memory + f"Diogo: {message}\nAmanda: {answer}\n"
    save_memory(user_id, updated_memory)
    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)