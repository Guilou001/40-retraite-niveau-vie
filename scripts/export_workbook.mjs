import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const root=path.resolve(process.argv[2] ?? '.');
const data=JSON.parse(await fs.readFile(path.join(root,'results/workbook_data.json'),'utf8'));
const workbook=Workbook.create();
const previews=path.join(root,'.cache/workbook-previews');
await fs.mkdir(previews,{recursive:true});
function base(name,title,subtitle,lastRow,lastColumn){
  const sheet=workbook.worksheets.add(name);
  sheet.showGridLines=false;
  sheet.getRangeByIndexes(0,0,lastRow,lastColumn).format.font={name:'Arial',size:10,color:'#263746'};
  sheet.getRangeByIndexes(0,0,lastRow,lastColumn).format.rowHeight=22;
  sheet.getRangeByIndexes(0,0,lastRow,lastColumn).format.columnWidth=22;
  sheet.getRangeByIndexes(0,0,lastRow,1).format.columnWidth=39;
  sheet.getRange('A2').values=[[title]];
  sheet.getRange('A2').format.font={name:'Arial',size:15,bold:true,color:'#263746'};
  sheet.getRange('A4').values=[[subtitle]];
  sheet.getRange('A4').format.font={name:'Arial',size:10,italic:true,color:'#526274'};
  sheet.getRange('A5').values=[['Les tableaux sont des résultats calculés. L’exemple contient des formules modifiables.']];
  return sheet;
}
for(const t of data.tables){
  const count=t.headers.length;
  const sheet=base(t.name,data.title,t.subtitle,t.rows.length+14,count+1);
  const rows=[t.headers,...t.rows];
  sheet.getRangeByIndexes(6,0,rows.length,count).values=rows;
  const header=sheet.getRangeByIndexes(6,0,1,count);
  header.format={fill:'#17659A',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,horizontalAlignment:'center',verticalAlignment:'center',rowHeight:62};
  for(let j=0;j<count;j++){
    const range=sheet.getRangeByIndexes(7,j,t.rows.length,1);
    range.setNumberFormat(t.formats[j]);
    range.format.horizontalAlignment=t.formats[j]==='@'?'left':'right';
  }
  for(let i=0;i<t.rows.length;i++){
    if(i%2===1)sheet.getRangeByIndexes(7+i,0,1,count).format.fill='#F1F5F8';
  }
  if(t.rows.length>12)sheet.freezePanes.freezeRows(7);
  const sourceRow=t.rows.length+10;
  sheet.getRange(`A${sourceRow}`).values=[['Sources, unités et conditions de réutilisation']];
  sheet.getRange(`A${sourceRow+1}`).values=[[data.repository+'/blob/main/docs/DONNEES.md']];
  const preview=await workbook.render({sheetName:t.name,range:`A1:${String.fromCharCode(64+count+1)}${sourceRow+2}`,scale:1.2,format:'png'});
  await fs.writeFile(path.join(previews,t.name+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
const example=data.example;
const sheet=base(example.name,example.title,example.subtitle,26,7);
sheet.getRange('A1:A26').format.columnWidth=54;
sheet.getRange('B1:B26').format.columnWidth=23;
sheet.getRange('A5').values=[['Bleu, hypothèse modifiable. Noir, résultat recalculé par une formule.']];
for(const cell of example.cells){
  sheet.getRange(`A${cell.row}`).values=[[cell.label]];
  const target=sheet.getRange(`B${cell.row}`);
  if(cell.formula){target.formulas=[[cell.formula]];target.format.font={color:'#202020',bold:true};}
  else {target.values=[[cell.value]];target.format.font={color:'#17659A'};target.format.fill='#EDF4FA';}
  target.setNumberFormat(cell.format);
}
sheet.getRange('A21').values=[['Exemple arithmétique du projet, distinct des résultats historiques.']];
sheet.getRange('A23').values=[[data.repository+'/blob/main/docs/COMPRENDRE.md']];
workbook.recalculate();
for(const [address,expected] of Object.entries(example.checks)){
  const actual=sheet.getRange(address).values[0][0];
  if(typeof actual!=='number'||Math.abs(actual-expected)>1e-9)throw new Error(`Résultat incorrect ${address} ${actual} au lieu de ${expected}`);
}
const mutation=example.mutation;
if(mutation){
  const input=sheet.getRange(mutation.input);
  const original=input.values[0][0];
  input.values=[[mutation.value]];
  workbook.recalculate();
  const result=sheet.getRange(mutation.output).values[0][0];
  if(typeof result!=='number'||Math.abs(result-mutation.expected)>1e-9)throw new Error('L’exemple ne réagit pas correctement à la modification de son hypothèse');
  input.values=[[original]];
  workbook.recalculate();
}
const scan=await workbook.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!',options:{useRegex:true,maxResults:30},maxChars:1500});
console.log(scan.ndjson);
const preview=await workbook.render({sheetName:'Exemple',range:'A1:G24',scale:1.2,format:'png'});
await fs.writeFile(path.join(previews,'Exemple.png'),new Uint8Array(await preview.arrayBuffer()));
const exported=await SpreadsheetFile.exportXlsx(workbook);
await exported.save(path.join(root,'results/resultats.xlsx'));
console.log('Classeur enregistré',root);
