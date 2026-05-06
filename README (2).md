# RemotePC v2 — Windows 🖥️📱

Controle completo do PC pelo celular via WiFi, com PIN de segurança.

---

## Arquivos necessários (ambos na mesma pasta)

- `remotepc_server.py` — rode no PC
- `remotepc_app.html` — servido automaticamente ao celular

---

## Instalação (uma vez só)

Abra o **Prompt de Comando** ou **PowerShell** e rode:
```
pip install websockets pynput
```

---

## Como usar

### 1. Configurar o PIN (opcional mas recomendado)

Abra `remotepc_server.py` em um editor de texto e mude a linha:
```python
PIN = "1234"   # ← coloque seu PIN aqui
```

### 2. Iniciar no PC

```
python remotepc_server.py
```

Vai aparecer:
```
  IP  : 192.168.1.100
  PIN : 1234
  Celular → http://192.168.1.100:8766
```

### 3. No celular (iOS ou Android)

1. Abra o Safari ou Chrome
2. Acesse o endereço exibido: `http://192.168.1.100:8766`
3. Digite o IP do PC e toque em **Conectar**
4. Digite o PIN quando solicitado
5. Pronto — 3 telas disponíveis!

> 💡 **iOS**: Compartilhar → "Adicionar à Tela de Início" = ícone como app nativo

---

## O que tem no app

### 🎮 Tela: Controle Remoto
| Função | |
|---|---|
| Play / Pause | Botão grande central |
| Próxima / Anterior | Botões de mídia |
| Volume +/−/Mudo | Seção volume |
| Brilho +/− | Seção brilho (via PowerShell) |
| Setas / OK | D-pad de navegação |
| Tela Cheia (F11) | Atalhos |
| Alt+Tab | Trocar janela |
| Desktop (Win+D) | Minimizar tudo |
| Sistema | Desligar / Reiniciar / Suspender / Bloquear |

### 🖱️ Tela: Mouse
| Função | |
|---|---|
| Trackpad | Deslize 1 dedo |
| Clique esquerdo | Toque rápido no trackpad |
| Duplo clique | 2 toques rápidos |
| Clique direito | Botão dedicado |
| Scroll | 2 dedos no trackpad |
| Scroll +/− | Botões de scroll |
| Click central | Botão dedicado |
| Copiar / Colar | Atalhos rápidos |

### ⌨️ Tela: Teclado
| Função | |
|---|---|
| Teclado QWERTY completo | Todas as letras |
| Modificadores | Ctrl, Alt, Shift, Win (travados) |
| Teclas de função | F1–F12 |
| Navegação | Home, End, PgUp, PgDn, setas |
| Numérico | 0–9 + operadores |
| Atalhos rápidos | Ctrl+C/V/X/Z/S/A/F, Alt+F4, Alt+Tab, etc. |
| Campo de texto | Digita texto longo direto no PC |

---

## Firewall Windows

Se não conectar, libere as portas. Abra **PowerShell como Administrador**:
```
netsh advfirewall firewall add rule name="RemotePC" dir=in action=allow protocol=TCP localport=8765,8766
```

---

## Brilho não funciona?

O controle de brilho usa WMI do Windows e pode não funcionar em monitores externos (HDMI). Funciona bem em monitores de notebook. Para monitor externo, use os botões físicos dele.

---

## Segurança

- PIN protege contra conexões não autorizadas na mesma rede
- Só aceita conexões locais (não expõe para internet)
- Mude o PIN padrão `1234` para algo diferente
