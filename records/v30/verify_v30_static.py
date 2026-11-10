#!/usr/bin/env python3
"""Static language/proposition migration checks only; no SUT or archive scripts.
Checks compare text identities and inventories, not mathematical validity.
"""
from pathlib import Path
import argparse,collections,difflib,hashlib,json,re

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def displays(s): return re.findall(r'\$\$.*?\$\$',s,re.S)
def inline(s): return re.findall(r'(?<!\$)\$(?!\$)([^$]+)\$(?!\$)',re.sub(r'\$\$.*?\$\$','',s,flags=re.S))
def tables(s): return re.findall(r'(?:^\|.*(?:\n|$))+',s,re.M)
def nums(s): return re.findall(r'[-−+]?\d+(?:\.\d+)?(?:[eE][−+\-]?\d+)?(?:[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)?',s)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path);ap.add_argument('--output',type=Path);a=ap.parse_args()
 root=Path(__file__).resolve().parent;m=json.loads((root/'v30_migration.json').read_text());bp=a.baseline or root/m['baseline'];fp=root/m['manuscript'];b=bp.read_text();s=fp.read_text();checks=[]
 def check(name,ok,detail=''):checks.append({'check':name,'passed':bool(ok),'detail':detail})
 check('baseline_identity',sha(bp)==m['baseline_sha256']=='6d45b9a106bfb665939b0269a3f571e513230839ce764fab51d623d684139d70')
 check('manuscript_identity',sha(fp)==m['manuscript_sha256'])
 bf,sf=displays(b),displays(s);check('display_count_17',len(bf)==len(sf)==17)
 check('display_multiset_identity',collections.Counter(bf)==collections.Counter(sf))
 for row in m['formula_mapping']:
  check('display_'+str(row['baseline_index'])+'_mapping',bf[row['baseline_index']-1]==row['formula']==sf[row['final_index']-1])
 check('inline_math_multiset_identity',collections.Counter(inline(b))==collections.Counter(inline(s)))
 br=re.findall(r'^\[\d+\] .*$',b,re.M);sr=re.findall(r'^\[\d+\] .*$',s,re.M)
 check('reference_count_43',len(br)==len(sr)==43)
 notes={x['id']:x for x in m['reference_note_migrations']}
 for i,row in enumerate(m['preserved_references']):
  note=notes.get(i+1)
  ok=(br[i]==row==sr[i]) if note is None else (br[i]==row==note['baseline_reference'] and sr[i]==note['final_reference'] and br[i].split('（')[0].rstrip()==sr[i].split('（')[0].rstrip())
  check('reference_'+str(i+1)+'_metadata_and_note_mapping',ok)
 check('reference_note_migration_file',json.loads((root/'书目阅读注迁移_v30.json').read_text())['migrations']==m['reference_note_migrations'])
 check('RQ_verbatim',re.findall(r'^- \*\*RQ.*$',b,re.M)==m['preserved_RQs']==re.findall(r'^- \*\*RQ.*$',s,re.M))
 bt,st=tables(b),tables(s);check('table_count',len(bt)==len(st)==len(m['table_mapping'])==46)
 for row in m['table_mapping']:
  i=row['index']-1;check('table_'+str(i+1)+'_mapped',bt[i]==row['baseline'] and st[i]==row['final'])
  check('table_'+str(i+1)+'_numbers',nums(bt[i])==nums(st[i]),'Numeric-token comparison supports review; it is not semantic proof.')
 removed_notes=' '.join(x['moved_reading_note'] for x in m['reference_note_migrations'])
 check('numeric_inventory_retained_or_reading_note_moved',set(nums(b))<=set(nums(s))|set(nums(removed_notes)),'Existence inventory only; numeric semantics require manual review. Reading-note tokens are separately traceable.')
 check('chapter_2_3_exact','### 2.3 假阳性（误报）：正确程序违反 MR' in s)
 check('chapter_2_4_exact','### 2.4 假阴性（漏检）：错误程序通过 MR' in s)
 check('execution_error_distinguished','程序有缺陷但本次输出未受影响，不属于这里的漏检' in s)
 check('violation_is_real','关系确实被违反；误报在于把这种违反认作程序错误' in s)
 maintext=s.split('## 数据、材料与AI辅助声明')[0]
 for term in ['贯穿例','依次回答','本文要预测的对象','本轮','叙事重组','卡K1','主稿']:
  check('no_main_drafting_label_'+term,term not in maintext)
 sec=s.split('#### 3.3.2 条件命题')[1].split('#### 3.3.3')[0]
 for i in range(1,5):
  check('proposition_'+str(i)+'_one_formal_statement',len(re.findall(r'\*\*命题'+str(i)+r'（',s))==1 and '**命题'+str(i)+'（' in sec)
  check('proposition_'+str(i)+'_appendix_proof','**命题'+str(i)+'的证明' in s.split('## 附录E')[1])
 check('corollary_one',s.count('**推论1（')==1)
 check('proof_map_exists',(root/'命题与证明对应_v30.md').is_file())
 check('formal_restatements_registered',len(m['new_formal_restating'])==5)
 check('no_control_char_artifacts',all(ord(c)>=32 or c in '\n\t' for c in s) and not s.rstrip().endswith('\\n'))
 check('diff_exact',(root/'v29_to_v30.diff').read_text()==''.join(difflib.unified_diff(b.splitlines(True),s.splitlines(True),fromfile='v29/'+bp.name,tofile='v30/'+fp.name)))
 check('heading_registry',m['headings']==[{'line':i,'heading':x} for i,x in enumerate(s.splitlines(),1) if x.startswith('#')])
 check('length_registry',m['size']['v29_full']==len(b) and m['size']['v30_full']==len(s) and m['size']['v29_main']==len(b.split('## 数据、材料与AI辅助声明')[0]) and m['size']['v30_main']==len(maintext))
 section_ids=set(re.findall(r'^#{2,4} (\d+(?:\.\d+)*)\s',s,re.M));pointers=set(re.findall(r'§(\d+(?:\.\d+)*)',maintext));check('main_section_targets',pointers<=section_ids,str(sorted(pointers-section_ids)))
 check('execution_scope_record',all(v is False for v in m['scope'].values()),'Recorded activity scope; no process instrumentation.')
 result={'schema':'v30-static/1.0','manuscript_sha256':sha(fp),'checker_sha256':sha(Path(__file__)),'passed':sum(x['passed'] for x in checks),'total':len(checks),'all_passed':all(x['passed'] for x in checks),'scope':'New standard-library text/hash comparison only. Does not prove scientific equivalence, capture identity, theorem validity or experiment reproduction.','checks':checks}
 if a.output:a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['passed','total','all_passed']}|{'failed':[x for x in checks if not x['passed']]},ensure_ascii=False));return 0 if result['all_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
