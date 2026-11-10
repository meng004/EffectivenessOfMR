#!/usr/bin/env python3
"""Read-only text/hash verification for v29. No scientific/package code is run.
Only --output writes a JSON report. Passing these checks is not a proof audit.
"""
import argparse, difflib, hashlib, json, re
from pathlib import Path

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def tables(text): return re.findall(r'(?:^\|.*(?:\n|$))+', text, re.M)
def refs(text): return {k:v for k,v in re.findall(r'^\[(\d+)\] (.*)$',text,re.M)}
def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--baseline',type=Path);a.add_argument('--output',type=Path)
    args=a.parse_args();root=Path(__file__).resolve().parent
    m=json.loads((root/'v29_migration.json').read_text());baseline=args.baseline or root/m['baseline'];f=root/m['manuscript']
    b=baseline.read_text();s=f.read_text();checks=[]
    def check(name,ok,detail=''): checks.append({'check':name,'passed':bool(ok),'detail':detail})
    check('baseline_identity',digest(baseline)==m['baseline_sha256']=='3b2941c279a8d8945a71be97f9d4679fbdb95c11b0b2096f106e70d46c31ecb1')
    check('manuscript_identity',digest(f)==m['manuscript_sha256'])
    check('plan_identity',digest(root/'修复计划与验收标准_v29.md')==m['plan_sha256'])
    bf=re.findall(r'\$\$.*?\$\$',b,re.S);sf=re.findall(r'\$\$.*?\$\$',s,re.S)
    check('display_formula_count',len(bf)==len(sf)==len(m['formula_mapping'])==17)
    for i,row in enumerate(m['formula_mapping']):
        check(row['id']+'_verbatim_order',bf[i]==row['formula']==sf[i] and row['v29_display_index']==i+1)
    for row in m['protected_data_tables']:
        t=row['baseline_table'];check(row['id']+'_data_table_preserved',t in b and t in s)
    check('protected_table_count',len(m['protected_data_tables'])==20)
    br=refs(b);sr=refs(s);check('references_count',len(br)==len(sr)==43)
    for k,line in m['original_references'].items():
        expected='['+k+'] '+br.get(k,'');actual='['+k+'] '+sr.get(k,'')
        check('reference_'+k+'_identity',expected==line==actual)
    # Checks are existence/identity tests, not semantic verification of the propositions.
    headings=[{'line':i,'heading':l} for i,l in enumerate(s.splitlines(),1) if l.startswith('#')]
    check('heading_registry',headings==m['headings'])
    section_ids=set(re.findall(r'^#{2,4} (\d+(?:\.\d+)*|[A-F](?:\.\d+)+)(?:\s|$)',s,re.M))
    pointers=set(re.findall(r'§(\d+(?:\.\d+)*)',s.split('## 参考文献')[0]))
    check('main_numeric_section_targets',pointers<=section_ids,str(sorted(pointers-section_ids)))
    expected_diff=''.join(difflib.unified_diff(b.splitlines(True),s.splitlines(True),fromfile='v28/'+baseline.name,tofile='v29/'+f.name))
    check('unified_diff_exact',(root/'v28_to_v29.diff').read_text()==expected_diff)
    size=m['main_text_size'];bn=len(b.split('## 数据、材料与AI辅助声明')[0]);sn=len(s.split('## 数据、材料与AI辅助声明')[0])
    check('main_character_counts',size['v28']==bn and size['v29']==sn and size['delta']==sn-bn)
    check('execution_boundary_record',all(v is False for v in m['execution_boundary'].values()),'Declared scope; does not instrument a running process.')
    checks_text={
      'gap_hypothesis_chain':['G1','G2','G3','H1／G1','H2／G2','H3／G3','全部相关前提、界与对象绑定成立'],
      'reuse_products':['Ⅰ-a 有理零块保持','Ⅰ-b 正路径信号资格','Ⅱ-a 完整MOC尺度传递','Ⅱ-b 固定源作用后残差','贡献Ⅲ支撑接口','贡献Ⅲ操作与记录','卡K1'],
      'shared_target_premises':['同一A、T及同一冻结r','TA0和TA1谱上均无极点','每个工作配置配对内核同一A、T、q_IPF及零源'],
      'complement_boundaries':['W计为新MR','P并未补足Z对ET的漏检','互补不保证全检','未执行提议'],
      'preserved_evidence_limits':['完整包围链未独立闭合','全状态','前瞻','真实三端'],
      'corrected_citation':['正系统的零模式与可达性[10,12]、功能等变[7]和结构保持数值积分[35]'],
    }
    for name,terms in checks_text.items(): check(name,all(t in s for t in terms),'; '.join(t for t in terms if t not in s))
    check('no_literal_newline_artifacts',not s.rstrip().endswith('\\n') and '\\n\\n###' not in s)
    check('no_stale_current_file_names','verify_v28_static.py' not in s and 'v28_migration.json' not in s)
    archive=root/'baseline_v28/evidence/v25_N1_final_review_package.zip'
    check('original_scientific_archive_identity',archive.is_file() and digest(archive)=='45dc02cb2223aa5f5bc9bb2622f289b251a1e190fe9ae145a05464171c3ec15e')
    result={'schema':'v29-static-check/1.0','manuscript_sha256':digest(f),'checker_sha256':digest(Path(__file__)),'scope':'New standard-library text/hash checks only; no SUT, archive scripts, scientific recomputation, or certificate regeneration. Existence tests do not establish scientific correctness.','passed':sum(x['passed'] for x in checks),'total':len(checks),'all_passed':all(x['passed'] for x in checks),'checks':checks}
    if args.output: args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'total':result['total'],'all_passed':result['all_passed'],'failed':[x for x in checks if not x['passed']]},ensure_ascii=False))
    return 0 if result['all_passed'] else 1
if __name__=='__main__': raise SystemExit(main())
