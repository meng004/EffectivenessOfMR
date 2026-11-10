#!/usr/bin/env python3
"""Static text/metadata preservation only. Never execute or import evidence code."""
from pathlib import Path
import argparse,hashlib,json,re,sys,difflib
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser()
ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
ap.add_argument('--baseline',type=Path)
ap.add_argument('--evidence',type=Path)
ap.add_argument('--output',type=Path)
a=ap.parse_args();root=a.root.resolve();m=json.loads((root/'v28_migration.json').read_text())
base=a.baseline or root/m['baseline'];draft=root/m['manuscript'];evidence=a.evidence or root/'evidence/v25_N1_final_review_package.zip'
b=base.read_text();s=draft.read_text();checks=[]
def ck(name,ok,detail=None):checks.append({'name':name,'passed':bool(ok),'detail':detail})
ck('baseline_sha',sha(base)==m['baseline_sha256'],sha(base))
ck('manuscript_sha',sha(draft)==m['manuscript_sha256'],sha(draft))
ck('original_scientific_zip_sha',evidence.is_file() and sha(evidence)=='45dc02cb2223aa5f5bc9bb2622f289b251a1e190fe9ae145a05464171c3ec15e')
oe=re.findall(r'\$\$.*?\$\$',b,re.S);ne=re.findall(r'\$\$.*?\$\$',s,re.S)
ck('exactly_17_display_equations',len(oe)==len(ne)==17)
for i,row in enumerate(m['formula_mapping']):
 ck(row['id']+'_verbatim_once',oe[i]==row['formula'] and ne.count(row['formula'])==1 and ne.index(row['formula'])+1==row['v28_display_index'])
def norm(t):
 pattern=r'§3\.(?:5\.[123]|6\.[12]|7\.[12]|[23567])(?![\d.])'
 t=re.sub(pattern,lambda z:m['internal_reference_mapping'][z.group()],t)
 return t.replace('| §3解析反例及残差分解 |','| 附录E的解析反例及残差分解 |')
for row in m['protected_data_tables']:
 ck(row['id']+'_data_table_preserved',row['v27_table'] in b and norm(row['v27_table']) in s)
pat=r'\d+(?:\.\d+)?(?:×10[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+|[eE][−-]?\d+)'
missing=sorted(set(re.findall(pat,b))-set(re.findall(pat,s)))
ck('original_scientific_number_tokens_retained',not missing,missing)
for i,row in m['original_references'].items():
 v=re.search(r'^\['+i+r'\] .*$',s,re.M)
 ck('original_reference_'+i+'_verbatim',v is not None and v.group()==row and re.search(r'^\['+i+r'\] .*$',b,re.M).group()==row)
sources=json.loads((root/'来源核对与阅读范围_v28.json').read_text())
for n,item in zip(range(36,40),sources['literature']):
 v=re.search(r'^\['+str(n)+r'\] .*$',s,re.M);line=v.group() if v else ''
 ck('new_reference_'+str(n)+'_metadata',all(t in line for t in item['authors']+[item['title'],item['doi'],str(item['year'])]))
for item in m['prior_reports']:
 p=root/item['path'];ck('prior_report_'+p.name,p.is_file() and sha(p)==item['sha256'])
ck('43_references_once',re.findall(r'^\[(\d+)\] ',s,re.M)==[str(i) for i in range(1,44)])
heads=[{'line':i,'heading':l} for i,l in enumerate(s.splitlines(),1) if l.startswith('#')]
ck('heading_registry',heads==m['v28_headings'])
hnums={z.group(1) for z in re.finditer(r'^#+ ([0-9]+(?:\.[0-9]+)*) ',s,re.M)}
main=s[:s.index('## 参考文献')]
missing_refs=sorted(set(re.findall(r'§([0-9]+(?:\.[0-9]+)*)',main))-hnums)
ck('main_internal_numeric_targets_exist',not missing_refs,missing_refs)
appheads={z.group(1) for z in re.finditer(r'^#+ (E\.[0-9]+(?:\.[0-9]+)*) ',s,re.M)}
apprefs=set(re.findall(r'附录(E\.[0-9]+(?:\.[0-9]+)*)',s))
ck('technical_appendix_targets_exist',not(apprefs-appheads),sorted(apprefs-appheads))
for n in range(1,5):ck('proposition_'+str(n)+'_once',len(re.findall(r'\*\*命题'+str(n)+r'（',s))==1)
for name,tokens in {
'new_induction_provenance':['B的图结构→本稿自含两端化','A不变族作事后解释','A的S3提供定性保序线索','A/B只讨论燃耗','A/B没有登记输运实例'],
'boundary_source_and_database':['有源时还须wᵀb=0','固定同一非零入流','未验证评价核数据','加载数据相关模块不等于'],
'three_numerical_standards':['MOC驱动的收敛阈值1e−8','max_iters=1000','M1/M2允许E≤0.01','M3允许E≤0.001','M1/M2尺度τ=0.04','M3尺度τ=0.01'],
'retained_qualification':['这组充分界允许的阈值集合','不是实际可分离的必要条件','M1的所有保证性预算及W解释','未完成独立前瞻预测','不报告总体预测准确率','三份MOC作者衍生正文'],
'recent_neighbors_scope':['生成阶段联合考虑误报／漏检','过滤误报','NIER论文','Industry论文'],
'current_navigation':['结构MR离散后有效性预测_修订稿_v28.md','修改说明_v28.md','v28_migration.json','verify_v28_static.py'],
}.items():ck(name,all(t in s for t in tokens),[t for t in tokens if t not in s])
expected=''.join(difflib.unified_diff(b.splitlines(True),s.splitlines(True),fromfile='v27/结构MR离散后有效性预测_重构稿_v27.md',tofile='v28/'+draft.name))
ck('unified_diff_current',(root/'v27_to_v28.diff').read_text()==expected)
size=m['main_text_size'];nold=len(b[:b.index('## 数据、材料与AI辅助声明')]);nnew=len(s[:s.index('## 数据、材料与AI辅助声明')])
ck('main_text_character_measure',nold==size['v27_chars'] and nnew==size['v28_chars'],{'v27':nold,'v28':nnew})
ck('execution_boundary_false',all(x is False for x in m['execution_boundary'].values()))
out={'schema':'v28-static-verification/1.0','all_passed':all(c['passed'] for c in checks),'passed':sum(c['passed'] for c in checks),'total':len(checks),'manuscript':draft.name,'manuscript_sha256':sha(draft),'checker_sha256':sha(Path(__file__)),'scope':'Static text/metadata only: 17 formula bytes, 13 data tables after explicit section-reference migration, original bibliography, selected scientific number tokens, new metadata, navigation and diff. Not proof validity, interval/certificate regeneration, source-PDF verification, SUT identity or prospective evaluation.','checks':checks}
txt=json.dumps(out,ensure_ascii=False,indent=2)
if a.output:a.output.write_text(txt+'\n')
else:print(txt)
sys.exit(0 if out['all_passed'] else 1)
