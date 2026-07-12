with open('requirements.txt', 'r', encoding='utf-16') as f: lines = f.readlines() 
clean_lines = [l.strip() for l in lines if 'mediapipe==' not in l and l.strip()] 
with open('requirements_clean.txt', 'w', encoding='utf-8') as f: f.write('\n'.join(clean_lines)) 
