"""Run: python -m cvflow --help."""
import argparse
import json
from pathlib import Path
from .documents import documents, read_document
from .pipeline import run, AUTHOR
from .report import render
from .review import apply_review


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(bundle, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory/'results.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf-8')
    (directory/'report.html').write_text(render(bundle),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description='Evidence-based CV review — Arga Bona Simarmata')
    commands=parser.add_subparsers(dest='command',required=True)
    process=commands.add_parser('run',help='Extract and assess a CV or bounded ZIP batch')
    process.add_argument('input',type=Path)
    process.add_argument('--job',type=Path,required=True)
    process.add_argument('--mode',choices=['mock','ollama'],default='mock')
    process.add_argument('--fixture',type=Path)
    process.add_argument('--model')
    process.add_argument('--limit',type=int,default=1)
    process.add_argument('--out',type=Path,default=Path('output/run'))
    review=commands.add_parser('review',help='Validate a review receipt and recompute corrected facts')
    review.add_argument('--results',required=True,type=Path)
    review.add_argument('--receipt',required=True,type=Path)
    review.add_argument('--source',required=True,type=Path)
    review.add_argument('--job',required=True,type=Path)
    review.add_argument('--out',type=Path,default=Path('output/reviewed'))
    commands.add_parser('demo',help='Run synthetic example, correction workflow and evaluation')
    commands.add_parser('evaluate',help='Evaluate labeled synthetic fixtures')
    args=parser.parse_args()
    try:
        if args.command in {'demo','evaluate'}:
            from .evaluation import evaluate, demo
            (demo if args.command=='demo' else evaluate)()
            return
        if args.command=='run':
            if args.mode=='mock' and not args.fixture:
                parser.error('Mock mode requires --fixture; use demo for a ready-to-run sample')
            if args.mode=='mock' and args.input.suffix.lower()=='.zip':
                parser.error('Mock fixture belongs to one CV. Use individual synthetic samples or Ollama for ZIP.')
            if args.mode=='ollama' and not args.model:
                parser.error('Ollama mode requires --model')
            job=load(args.job)
            results=[run(text,f'C-{i:04d}',name,job,mode=args.mode,model=args.model,fixture=args.fixture,input_error=error)
                     for i,(name,text,error) in enumerate(documents(args.input,args.limit),1)]
            bundle={'author':AUTHOR,'job':job,'results':results}
            save(bundle,args.out)
            failures=sum(r['processing_status']=='failed' for r in results)
            print(f'{len(results)} processed, {failures} failed. Report: {(args.out/"report.html").resolve()}')
            if failures:
                raise SystemExit(2)
        else:
            bundle=load(args.results);receipt=load(args.receipt);job=load(args.job)
            originals=[r for r in bundle['results'] if r['candidate_id']==receipt['candidate_id']]
            if len(originals)!=1:
                raise ValueError('Review must match exactly one candidate')
            target=args.out.resolve()
            if target==args.results.parent.resolve():
                raise ValueError('Review output must use a separate directory to preserve original results')
            reviewed=apply_review(originals[0],receipt,read_document(args.source),job)
            save({'author':AUTHOR,'job':job,'results':[reviewed['result']], 'review':reviewed['review']},args.out)
            (args.out/'review_receipt.json').write_text(json.dumps(reviewed,ensure_ascii=False,indent=2),encoding='utf-8')
            print(f'Review saved: {args.out.resolve()}')
    except (OSError,ValueError,KeyError) as exc:
        parser.error(str(exc))

if __name__=='__main__':
    main()
