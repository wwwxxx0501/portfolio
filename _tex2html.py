"""
Convert TeX document to structured HTML project pages matching the old b3c13ce UI style.
Handles: sections, subsections, paragraphs, code blocks, tables, figures, formulas, lists, infoboxes.
"""
import re, os, shutil, html

TEX_FILE = r"D:\projects\项目集说明_v2.tex"
TEX_IMG_ROOT = r"D:\1\大三下\杂七杂八\ws\xyw\材料经历"
PROJ_ROOT = r"D:\projects"
IMG_BASE = os.path.join(PROJ_ROOT, "assets", "images")
PROJECTS_DIR = os.path.join(PROJ_ROOT, "projects")

# Chapter config: section_title_prefix -> (html_file, folder_id, meta, abstract, keywords, videos)
CHAPTERS = {
    "RoboMaster": {
        "id": "robomaster", "file": "robomaster.html",
        "title_override": "RoboMaster 视觉伺服引擎（rm-engine）",
        "meta": ["薛雅文（工程组视觉第一负责人）", "重庆大学 RoboMaster 战队", "2024.09 – 2025.08"],
        "videos": [("robomaster.mp4", "机械臂视觉伺服系统实际运行演示")],
    },
    "SpeedyBot": {
        "id": "sweeping-robot", "file": "sweeping-robot.html",
        "title_override": "SpeedyBot 智能扫地机器人",
        "meta": ["薛雅文", "2024 – 2025"],
        "videos": [
            ("speedybot-slam.mp4", "全屋 SLAM 建图过程"),
            ("speedybot-nav.mp4", "自主导航与避障演示"),
            ("speedybot-comm.mp4", "自研通信协议调试"),
        ],
    },
    "工创赛": {
        "id": "tracking-car", "file": "tracking-car.html",
        "title_override": "工创赛——K210智能垃圾分类识别系统",
        "meta": ["薛雅文（队长）", "2024 – 2025"],
        "videos": [],
    },
    "电机驱动": {
        "id": "motor-driver", "file": "motor-driver.html",
        "title_override": "电机驱动综合系统",
        "meta": ["薛雅文", "2024 – 2025"],
        "videos": [],
    },
    "PCA": {
        "id": "face-recognition", "file": "face-recognition.html",
        "title_override": "PCA + SVM 人脸识别系统",
        "meta": ["薛雅文", "2024"],
        "videos": [],
    },
    "VHDL": {
        "id": "digital-logic", "file": "digital-logic.html",
        "title_override": "VHDL数字逻辑电路设计",
        "meta": ["薛雅文", "2024"],
        "videos": [],
    },
    "ADS1292R": {
        "id": "heart-rate", "file": "heart-rate.html",
        "title_override": "2020电赛C题——ADS1292R心电图检测仪",
        "meta": ["薛雅文", "2025"],
        "videos": [
            ("heart-rate-1.mp4", "心电信号采集演示 1"),
            ("heart-rate-2.mp4", "心电信号采集演示 2"),
        ],
    },
    "仿生": {
        "id": "desk-lamp", "file": "desk-lamp.html",
        "title_override": "仿生多模态智能台灯",
        "meta": ["薛雅文、郑皓文、严海轩、令狐子安", "2025 – 2026"],
        "videos": [("desk-lamp.mp4", "智能台灯功能演示")],
    },
    "机器人色块": {
        "id": "color-grabbing", "file": "color-grabbing.html",
        "title_override": "机器人色块识别与抓取",
        "meta": ["薛雅文", "2024"],
        "videos": [],
    },
    "FSBB": {
        "id": "fsbb", "file": "fsbb.html",
        "title_override": "FSBB尖峰补能系统",
        "meta": ["薛雅文", "2024 – 2025"],
        "videos": [],
    },
    "挑战杯": {
        "id": "challenge-cup", "file": "challenge-cup.html",
        "title_override": "挑战杯·青年养老赋能计划",
        "meta": ["薛雅文", "2024 – 2025"],
        "videos": [],
    },
    "QEA": {
        "id": "boat", "file": "boat.html",
        "title_override": "QEA电动船设计与稳性分析",
        "meta": ["薛雅文等（5人团队）", "2024"],
        "videos": [("boat.mp4", "电动船航行演示")],
    },
    "工程原理——激光": {
        "id": "pathplan", "file": "pathplan.html",
        "title_override": "工程原理——激光雷达路径规划系统",
        "meta": ["薛雅文", "2024"],
        "videos": [],
    },
    "SRTP": {
        "id": "srtp", "file": "srtp.html",
        "title_override": "SRTP 学生科研训练项目——电磁炮",
        "meta": ["薛雅文", "2024 – 2025"],
        "videos": [],
    },
    "圆形薄膜": {
        "id": "math-physics-method", "file": "math-physics-method.html",
        "title_override": "圆形薄膜振动的理论分析与实验验证",
        "meta": ["薛雅文", "2025"],
        "videos": [],
    },
    "救灾机器人": {
        "id": "ergonomics", "file": "ergonomics.html",
        "title_override": "救灾机器人人因分析",
        "meta": ["薛雅文", "2025"],
        "videos": [],
    },
    "Gamma": {
        "id": "stirling", "file": "stirling.html",
        "title_override": "工程设计课程项目——Gamma型斯特林发动机联合仿真",
        "meta": ["薛雅文", "2025"],
        "videos": [],
    },
    "CUPT": {
        "id": "fluid-levitation", "file": "fluid-levitation.html",
        "title_override": "2025 CUPT/IYPT/CYPT 8.悬浮液体",
        "meta": ["薛雅文", "2025"],
        "videos": [
            ("fluid-levitation/experiment-process.mp4", "实验流程"),
            ("fluid-levitation/experiment-phenomenon.mp4", "实验现象"),
        ],
    },
}

def read_tex():
    with open(TEX_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def split_chapters(tex):
    """Split TeX into chapter blocks by \\section{}"""
    pattern = r'\\section\{(.+?)\}'
    splits = list(re.finditer(pattern, tex))
    chapters = []
    for i, m in enumerate(splits):
        title = m.group(1)
        start = m.start()
        end = splits[i+1].start() if i+1 < len(splits) else len(tex)
        body = tex[start:end]
        chapters.append((title, body))
    return chapters

def find_chapter_config(title):
    """Match chapter title to config"""
    for prefix, cfg in CHAPTERS.items():
        if prefix in title:
            return cfg
    return None

# ---- Figure counter and used filenames per chapter ----
fig_counter = 0
used_filenames = {}  # Maps (chapter_id, basename) -> source_path

def resolve_image(tex_path, chapter_id):
    """Resolve TeX image path to web path, copying if needed."""
    global fig_counter
    fig_counter += 1
    
    # Clean up path
    tex_path = tex_path.strip().strip('"')
    
    # Try to find image in TEX_IMG_ROOT
    src = os.path.join(TEX_IMG_ROOT, tex_path)
    if not os.path.exists(src):
        # Try common variations
        for ext in ['.png', '.jpg', '.jpeg']:
            if os.path.exists(src + ext):
                src = src + ext
                break
    
    if not os.path.exists(src):
        print(f"  WARNING: Image not found: {tex_path}")
        return None
    
    src = os.path.normpath(src)
    
    # Determine destination - handle duplicate filenames within same chapter
    fname = os.path.basename(src)
    dest_dir = os.path.join(IMG_BASE, chapter_id)
    os.makedirs(dest_dir, exist_ok=True)
    
    key = (chapter_id, fname)
    if key in used_filenames and used_filenames[key] != src:
        # Same filename from different source in same chapter - add suffix
        base, ext = os.path.splitext(fname)
        counter = 2
        while True:
            fname = f"{base}_{counter}{ext}"
            key = (chapter_id, fname)
            if key not in used_filenames:
                break
            counter += 1
    
    used_filenames[key] = src
    dest = os.path.join(dest_dir, fname)
    
    if not os.path.exists(dest):
        shutil.copy2(src, dest)
        print(f"  COPIED: {fname}")
    
    return f"../assets/images/{chapter_id}/{fname}"

def tex_to_html_inline(text):
    """Convert inline TeX markup to HTML"""
    # Remove comments
    text = re.sub(r'(?<!\\)%.*', '', text)
    
    # textbf -> strong
    text = re.sub(r'\\textbf\{([^}]*)\}', r'<strong>\1</strong>', text)
    # textit -> em
    text = re.sub(r'\\textit\{([^}]*)\}', r'<em>\1</em>', text)
    # texttt -> code
    text = re.sub(r'\\texttt\{([^}]*)\}', r'<code>\1</code>', text)
    # emph -> em
    text = re.sub(r'\\emph\{([^}]*)\}', r'<em>\1</em>', text)
    # code -> code (inline)
    text = re.sub(r'\\code\{([^}]*)\}', r'<code>\1</code>', text)
    
    # Math: $...$ -> inline
    text = re.sub(r'\$([^$]+)\$', r'<em class="math">\1</em>', text)
    
    # LaTeX special chars
    text = text.replace('\\&', '&amp;')
    text = text.replace('\\%', '%')
    text = text.replace('\\#', '#')
    text = text.replace('\\$', '$')
    text = text.replace('``', '"')
    text = text.replace("''", '"')
    text = text.replace('---', '—')
    text = text.replace('--', '–')
    text = text.replace('\\\\', '<br>')
    text = text.replace('\\newline', '<br>')
    text = text.replace('~', ' ')
    text = text.replace('\\,', ' ')
    text = text.replace('\\;', ' ')
    text = text.replace('\\!', '')
    text = text.replace('\\quad', '  ')
    text = text.replace('\\qquad', '    ')
    text = text.replace('\\ldots', '…')
    text = text.replace('\\dots', '…')
    text = text.replace('\\times', '×')
    text = text.replace('\\sim', '~')
    text = text.replace('\\leq', '≤')
    text = text.replace('\\geq', '≥')
    text = text.replace('\\neq', '≠')
    text = text.replace('\\pm', '±')
    text = text.replace('\\to', '→')
    text = text.replace('\\rightarrow', '→')
    text = text.replace('\\leftarrow', '←')
    text = text.replace('\\infty', '∞')
    text = text.replace('\\pi', 'π')
    text = text.replace('\\theta', 'θ')
    text = text.replace('\\phi', 'φ')
    text = text.replace('\\psi', 'ψ')
    text = text.replace('\\omega', 'ω')
    text = text.replace('\\alpha', 'α')
    text = text.replace('\\beta', 'β')
    text = text.replace('\\gamma', 'γ')
    text = text.replace('\\delta', 'δ')
    text = text.replace('\\epsilon', 'ε')
    text = text.replace('\\varepsilon', 'ε')
    text = text.replace('\\lambda', 'λ')
    text = text.replace('\\mu', 'μ')
    text = text.replace('\\sigma', 'σ')
    text = text.replace('\\rho', 'ρ')
    text = text.replace('\\Delta', 'Δ')
    text = text.replace('\\Omega', 'Ω')
    text = text.replace('\\sum', 'Σ')
    text = text.replace('\\prod', 'Π')
    text = text.replace('\\partial', '∂')
    text = text.replace('\\nabla', '∇')
    text = text.replace('\\approx', '≈')
    text = text.replace('\\circ', '°')
    text = text.replace('\\deg', '°')
    text = text.replace('\\gg', '≫')
    text = text.replace('\\ll', '≪')
    text = text.replace('\\cdot', '·')
    text = text.replace('\\sqrt', '√')
    text = text.replace('\\int', '∫')
    text = text.replace('\\forall', '∀')
    text = text.replace('\\exists', '∃')
    text = text.replace('\\cap', '∩')
    text = text.replace('\\cup', '∪')
    text = text.replace('\\in', '∈')
    text = text.replace('\\subset', '⊂')
    text = text.replace('\\log', 'log')
    text = text.replace('\\exp', 'exp')
    text = text.replace('\\sin', 'sin')
    text = text.replace('\\cos', 'cos')
    text = text.replace('\\tan', 'tan')
    
    # Handle \frac{a}{b} -> (a)/(b) - must be done before brace removal
    while '\\frac' in text:
        m = re.search(r'\\frac\s*\{', text)
        if not m:
            text = text.replace('\\frac', '')
            break
        pos = m.end()
        depth = 1
        while pos < len(text) and depth > 0:
            if text[pos] == '{': depth += 1
            elif text[pos] == '}': depth -= 1
            pos += 1
        num = text[m.end():pos-1]
        if pos < len(text) and text[pos] == '{':
            pos2 = pos + 1
            depth = 1
            while pos2 < len(text) and depth > 0:
                if text[pos2] == '{': depth += 1
                elif text[pos2] == '}': depth -= 1
                pos2 += 1
            den = text[pos+1:pos2-1]
            text = text[:m.start()] + f'({num})/({den})' + text[pos2:]
        else:
            text = text[:m.start()] + num + text[pos:]
            break
    
    # Sub/superscripts: simple cases
    text = re.sub(r'_\{([^}]*)\}', r'<sub>\1</sub>', text)
    text = re.sub(r'\^\{([^}]*)\}', r'<sup>\1</sup>', text)
    text = re.sub(r'_(\w)', r'<sub>\1</sub>', text)
    text = re.sub(r'\^(\w)', r'<sup>\1</sup>', text)
    
    # Remove remaining simple LaTeX commands
    text = re.sub(r'\\text\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\mathbf\{([^}]*)\}', r'<strong>\1</strong>', text)
    text = re.sub(r'\\operatorname\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\(?:left|right|big|Big|bigg|Bigg)[.()\[\]|]?', '', text)
    text = re.sub(r'\\(?:begin|end)\{[^}]*\}', '', text)
    text = re.sub(r'\\(?:centering|noindent|hfill|vspace|hspace)\{?[^}]*\}?', '', text)
    text = re.sub(r'\\label\{[^}]*\}', '', text)
    text = re.sub(r'\\ref\{[^}]*\}', '', text)
    text = re.sub(r'\\cite\{[^}]*\}', '', text)
    
    # Clean up stray backslashes
    text = re.sub(r'\\([a-zA-Z]+)', r'\1', text)
    
    # Clean up braces
    text = text.replace('{', '').replace('}', '')
    
    return text.strip()

def convert_equation(eq_text):
    """Convert a TeX equation block to HTML formula div"""
    # Simplify the equation for display
    eq = eq_text.strip()
    eq = tex_to_html_inline(eq)
    return f'    <div class="formula">{eq}</div>\n'

def convert_table(table_text, caption=""):
    """Convert a TeX tabular to HTML table"""
    lines = table_text.strip().split('\n')
    rows = []
    has_midrule = any('midrule' in l for l in lines)
    header_done = not has_midrule  # if no midrule, all rows are data
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('%'):
            continue
        if 'toprule' in line or 'bottomrule' in line:
            continue
        if 'midrule' in line:
            header_done = True
            continue
        if 'endhead' in line or 'endfirsthead' in line or 'endfoot' in line:
            continue
        if line.startswith('\\begin') or line.startswith('\\end'):
            continue
        if 'centering' in line or 'caption' in line:
            continue
        if '&' in line:
            cells = [tex_to_html_inline(c.strip().rstrip('\\').strip()) for c in line.replace('\\\\', '').split('&')]
            if not header_done:
                rows.append(('th', cells))
            else:
                rows.append(('td', cells))
    
    if not rows:
        return ''
    
    h = '    <table>\n'
    if caption:
        h += f'        <caption>{tex_to_html_inline(caption)}</caption>\n'
    
    for tag, cells in rows:
        h += '        <tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>\n'
    
    h += '    </table>\n'
    return h

def convert_code_block(code_text, caption=""):
    """Convert lstlisting to HTML code block"""
    # Extract the actual code (between begin/end)
    # Remove lstlisting options
    code = code_text
    code = re.sub(r'\\begin\{lstlisting\}\[.*?\]', '', code)
    code = re.sub(r'\\begin\{lstlisting\}', '', code)
    code = re.sub(r'\\end\{lstlisting\}', '', code)
    code = code.strip()
    
    # HTML escape
    code = html.escape(code)
    
    h = '    <div class="code-block">\n'
    if caption:
        cap = tex_to_html_inline(caption)
        h += f'        <div class="code-block-header">{cap}</div>\n'
    h += f'        <pre>{code}</pre>\n'
    h += '    </div>\n'
    return h

def convert_chapter(title, body, cfg):
    """Convert a chapter's TeX body to HTML content"""
    global fig_counter
    fig_counter = 0
    
    chapter_id = cfg["id"]
    result = []
    toc_entries = []  # [(level, number, title, anchor_id), ...]
    
    # Section numbering
    sec_num = 0
    subsec_num = 0
    subsubsec_num = 0
    
    # Process line by line with state tracking
    lines = body.split('\n')
    i = 0
    in_list = None  # 'ul' or 'ol'
    in_paragraph = False
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('%'):
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            i += 1
            continue
        
        # Skip the section title itself
        if line.startswith('\\section{'):
            i += 1
            continue
        
        # Subsection
        m = re.match(r'\\subsection\{(.+?)\}', line)
        if m:
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            if in_list:
                result.append(f'    </{in_list}>\n')
                in_list = None
            sec_num += 1
            subsec_num = 0
            subsubsec_num = 0
            title_text = tex_to_html_inline(m.group(1))
            anchor_id = f'sec-{sec_num}'
            toc_entries.append((2, str(sec_num), title_text, anchor_id))
            result.append(f'\n    <h2 id="{anchor_id}">{sec_num} &nbsp; {title_text}</h2>\n')
            i += 1
            continue
        
        # Subsubsection
        m = re.match(r'\\subsubsection\{(.+?)\}', line)
        if m:
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            if in_list:
                result.append(f'    </{in_list}>\n')
                in_list = None
            subsec_num += 1
            title_text = tex_to_html_inline(m.group(1))
            anchor_id = f'sec-{sec_num}-{subsec_num}'
            toc_entries.append((3, f'{sec_num}.{subsec_num}', title_text, anchor_id))
            result.append(f'\n    <h3 id="{anchor_id}">{sec_num}.{subsec_num} &nbsp; {title_text}</h3>\n')
            i += 1
            continue
        
        # Info box / result box / iter box
        if re.match(r'\\begin\{(infobox|resultbox|iterbox)\}', line):
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            # Extract title
            box_title = ""
            m2 = re.search(r'\[(.+?)\]', line)
            if m2:
                box_title = tex_to_html_inline(m2.group(1))
            
            # Collect box content
            box_lines = []
            depth = 1
            i += 1
            while i < len(lines) and depth > 0:
                bl = lines[i].strip()
                if re.match(r'\\begin\{(infobox|resultbox|iterbox)\}', bl):
                    depth += 1
                if re.match(r'\\end\{(infobox|resultbox|iterbox)\}', bl):
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                box_lines.append(bl)
                i += 1
            
            box_content = '\n'.join(box_lines)
            
            # Check if it's a tabular info box
            if '\\begin{tabular}' in box_content:
                result.append('    <div class="info-box">\n')
                if box_title:
                    result.append(f'        <div class="info-box-title">{box_title}</div>\n')
                result.append(convert_table(box_content))
                result.append('    </div>\n')
            elif '\\begin{enumerate}' in box_content or '\\begin{itemize}' in box_content:
                result.append('    <div class="info-box">\n')
                if box_title:
                    result.append(f'        <div class="info-box-title">{box_title}</div>\n')
                # Parse list
                items = re.findall(r'\\item\s*(.*?)(?=\\item|\\end)', box_content, re.DOTALL)
                if not items:
                    items = re.findall(r'\\item\s*(.*?)$', box_content, re.MULTILINE)
                tag = 'ol' if '\\begin{enumerate}' in box_content else 'ul'
                result.append(f'        <{tag}>\n')
                for item in items:
                    item_text = tex_to_html_inline(item.strip())
                    if item_text:
                        result.append(f'            <li>{item_text}</li>\n')
                result.append(f'        </{tag}>\n')
                result.append('    </div>\n')
            else:
                result.append('    <div class="info-box">\n')
                if box_title:
                    result.append(f'        <div class="info-box-title">{box_title}</div>\n')
                result.append(f'        <p>{tex_to_html_inline(box_content)}</p>\n')
                result.append('    </div>\n')
            continue
        
        # Figure environment
        if '\\begin{figure}' in line:
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            
            # Collect figure content
            fig_lines = []
            i += 1
            while i < len(lines):
                fl = lines[i].strip()
                if '\\end{figure}' in fl:
                    i += 1
                    break
                fig_lines.append(fl)
                i += 1
            
            fig_content = '\n'.join(fig_lines)
            
            # Check for subfigures
            subfigs = re.findall(r'\\begin\{subfigure\}.*?\\includegraphics.*?\{([^}]+)\}.*?\\caption\{([^}]*)\}.*?\\end\{subfigure\}', fig_content, re.DOTALL)
            
            if subfigs:
                result.append('    <div class="figure-row">\n')
                for sf_path, sf_cap in subfigs:
                    web_path = resolve_image(sf_path, chapter_id)
                    if web_path:
                        cap = tex_to_html_inline(sf_cap) if sf_cap else f"Fig. {fig_counter}"
                        result.append(f'        <div class="figure">\n')
                        result.append(f'            <img src="{web_path}" alt="{cap}" onclick="openLightbox(this)">\n')
                        result.append(f'            <div class="figure-caption">{cap}</div>\n')
                        result.append(f'        </div>\n')
                result.append('    </div>\n')
            else:
                # Single figure
                m_img = re.search(r'\\includegraphics.*?\{([^}]+)\}', fig_content)
                m_cap = re.search(r'\\caption\{(.+?)\}', fig_content)
                
                if m_img:
                    img_path = m_img.group(1)
                    web_path = resolve_image(img_path, chapter_id)
                    caption = tex_to_html_inline(m_cap.group(1)) if m_cap else f"Fig. {fig_counter}"
                    
                    if web_path:
                        result.append(f'    <div class="figure">\n')
                        result.append(f'        <img src="{web_path}" alt="{caption}" onclick="openLightbox(this)">\n')
                        result.append(f'        <div class="figure-caption">Fig. {fig_counter} &nbsp; {caption}</div>\n')
                        result.append(f'    </div>\n')
            continue
        
        # Standalone includegraphics (not in figure env)
        m = re.match(r'\\includegraphics.*?\{([^}]+)\}', line)
        if m:
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            img_path = m.group(1)
            web_path = resolve_image(img_path, chapter_id)
            if web_path:
                result.append(f'    <div class="figure">\n')
                result.append(f'        <img src="{web_path}" alt="Figure" onclick="openLightbox(this)">\n')
                result.append(f'    </div>\n')
            i += 1
            continue
        
        # Lstlisting (code block)
        if '\\begin{lstlisting}' in line:
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            
            # Extract caption from options
            cap = ""
            m_cap = re.search(r'caption\s*=\s*\{(.+?)\}', line)
            if m_cap:
                cap = m_cap.group(1)
            
            code_lines = []
            i += 1
            while i < len(lines):
                if '\\end{lstlisting}' in lines[i]:
                    i += 1
                    break
                code_lines.append(lines[i])
                i += 1
            
            result.append(convert_code_block('\n'.join(code_lines), cap))
            continue
        
        # Table environment
        if '\\begin{table}' in line or '\\begin{longtable}' in line:
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            
            table_lines = []
            cap = ""
            i += 1
            while i < len(lines):
                tl = lines[i].strip()
                if '\\end{table}' in tl or '\\end{longtable}' in tl:
                    i += 1
                    break
                m_cap = re.match(r'\\caption\{(.+?)\}', tl)
                if m_cap:
                    cap = m_cap.group(1)
                table_lines.append(tl)
                i += 1
            
            result.append(convert_table('\n'.join(table_lines), cap))
            continue
        
        # Center environment with tabular
        if '\\begin{center}' in line:
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            
            center_lines = []
            i += 1
            while i < len(lines):
                cl = lines[i].strip()
                if '\\end{center}' in cl:
                    i += 1
                    break
                center_lines.append(cl)
                i += 1
            
            center_content = '\n'.join(center_lines)
            if '\\begin{tabular}' in center_content or '\\begin{longtable}' in center_content:
                result.append(convert_table(center_content))
            else:
                result.append(f'    <div style="text-align:center">{tex_to_html_inline(center_content)}</div>\n')
            continue
        
        # Equation
        if '\\begin{equation' in line:
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            
            eq_lines = []
            i += 1
            while i < len(lines):
                el = lines[i].strip()
                if '\\end{equation' in el:
                    i += 1
                    break
                eq_lines.append(el)
                i += 1
            
            result.append(convert_equation('\n'.join(eq_lines)))
            continue
        
        # Align environment
        if '\\begin{align' in line:
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            
            eq_lines = []
            i += 1
            while i < len(lines):
                el = lines[i].strip()
                if '\\end{align' in el:
                    i += 1
                    break
                eq_lines.append(el)
                i += 1
            
            result.append(convert_equation('\n'.join(eq_lines)))
            continue
        
        # Itemize / enumerate
        if '\\begin{itemize}' in line or '\\begin{enumerate}' in line:
            if in_paragraph:
                result.append('</p>\n')
                in_paragraph = False
            
            tag = 'ol' if 'enumerate' in line else 'ul'
            # Collect all items until end
            list_lines = []
            depth = 1
            i += 1
            while i < len(lines) and depth > 0:
                ll = lines[i].strip()
                if '\\begin{itemize}' in ll or '\\begin{enumerate}' in ll:
                    depth += 1
                if '\\end{itemize}' in ll or '\\end{enumerate}' in ll:
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                list_lines.append(ll)
                i += 1
            
            list_content = '\n'.join(list_lines)
            items = re.split(r'\\item\s*', list_content)
            items = [it.strip() for it in items if it.strip()]
            
            result.append(f'    <{tag}>\n')
            for item in items:
                # Handle nested lists
                item_html = tex_to_html_inline(item.replace('\n', ' '))
                result.append(f'        <li>{item_html}</li>\n')
            result.append(f'    </{tag}>\n')
            continue
        
        # Skip various LaTeX commands
        if line.startswith('\\begin{') or line.startswith('\\end{'):
            i += 1
            continue
        if line.startswith('\\centering') or line.startswith('\\caption') or line.startswith('\\label'):
            i += 1
            continue
        if line.startswith('\\newpage') or line.startswith('\\clearpage'):
            i += 1
            continue
        if line.startswith('\\vspace') or line.startswith('\\hspace'):
            i += 1
            continue
        
        # Regular paragraph text
        if not in_paragraph:
            result.append('    <p>\n        ')
            in_paragraph = True
        
        result.append(tex_to_html_inline(line) + '\n        ')
        i += 1
    
    if in_paragraph:
        result.append('</p>\n')
    if in_list:
        result.append(f'    </{in_list}>\n')
    
    return ''.join(result), toc_entries

def build_toc_html(toc_entries):
    """Build a table-of-contents HTML block from heading entries."""
    if not toc_entries:
        return ''
    lines = ['    <nav class="toc">\n', '        <div class="toc-title">目录</div>\n', '        <ul>\n']
    for level, number, text, anchor in toc_entries:
        indent = '            ' if level == 3 else '        '
        cls = ' class="toc-sub"' if level == 3 else ''
        lines.append(f'{indent}<li{cls}><a href="#{anchor}">{number} &nbsp; {text}</a></li>\n')
    lines.append('        </ul>\n')
    lines.append('    </nav>\n')
    return ''.join(lines)

def generate_html(cfg, content_html, toc_entries=None):
    """Generate full HTML page"""
    title = cfg.get("title_override", "Project")
    meta_spans = ''.join(f'<span>{m}</span>' for m in cfg.get("meta", []))
    
    video_section = ""
    if cfg.get("videos"):
        video_section = f'\n    <h2>演示视频</h2>\n'
        for vf, vcap in cfg["videos"]:
            video_section += f'''    <div class="figure">
        <video controls style="width:100%; border-radius:4px;">
            <source src="../assets/videos/{vf}" type="video/mp4">
        </video>
        <div class="figure-caption">Video &nbsp; {vcap}</div>
    </div>\n'''
    
    toc_html = build_toc_html(toc_entries or [])

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>

<nav class="nav">
    <div class="nav-inner">
        <a class="nav-brand" href="../index.html">薛雅文 · Portfolio</a>
        <div class="nav-links">
            <a href="../index.html">首页</a>
            <a href="#" class="active">项目</a>
        </div>
    </div>
</nav>

<div class="container">
    <div class="article-header">
        <h1 class="article-title">{title}</h1>
        <div class="article-meta">
            {meta_spans}
        </div>
    </div>

{toc_html}
{content_html}
{video_section}
    <p style="margin-top:2rem; text-align:center;">
        <a href="../index.html">← 返回首页</a>
    </p>
</div>

<footer class="footer">&copy; 2025&ndash;2026 薛雅文 &middot; 重庆大学国家卓越工程师学院</footer>

<!-- Lightbox -->
<div class="lightbox" id="lightbox" onclick="this.classList.remove('active')">
    <img id="lightboxImg" src="" alt="">
</div>

<button class="back-top" id="backTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>
<script>
window.addEventListener('scroll', () => {{
    document.getElementById('backTop').classList.toggle('visible', window.scrollY > 300);
}});
function openLightbox(el) {{
    document.getElementById('lightboxImg').src = el.src;
    document.getElementById('lightbox').classList.add('active');
}}
</script>
</body>
</html>'''

def main():
    tex = read_tex()
    chapters = split_chapters(tex)
    
    print(f"Found {len(chapters)} chapters")
    
    for title, body in chapters:
        cfg = find_chapter_config(title)
        if not cfg:
            print(f"SKIP: {title} (no config)")
            continue
        
        print(f"\n=== {cfg['id']}: {title} ===")
        content_html, toc_entries = convert_chapter(title, body, cfg)
        full_html = generate_html(cfg, content_html, toc_entries)
        
        out_path = os.path.join(PROJECTS_DIR, cfg["file"])
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        print(f"  -> {cfg['file']} ({len(full_html)} bytes)")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
