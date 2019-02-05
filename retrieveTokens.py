import argparse
import csv
import requests
import time

from bs4 import BeautifulSoup

url = 'https://etherscan.io/tokens?p='

def main(outputFile, pagesCount):
   with open(outputFile, 'wt', newline='') as resultFile:
      w = csv.DictWriter(resultFile, fieldnames = ['address', 'ticker', 'marketCap', 'price', 'name'])
      w.writeheader()
      for pageNr in range(1,pagesCount+1):
         print('Scanning %s  out of %s' % (pageNr, pagesCount))
         pageResult = requests.get(url + str(pageNr))
         if pageResult.ok:
            tokensData = processPage(pageResult.content)
            w.writerows(tokensData)
            resultFile.flush()
         else:
            print (pageResult)
         time.sleep(0.3)
    
def processPage(content):
   page = BeautifulSoup(content, features="html.parser")
   results = []
   index  = 0
   for row in page.select('table')[0].select('tr'):
      if index != 0:
         cells = row.select('td')
         # cells[3].find('a') - token url, name and ticker:
         #      <a href="/token/0xB8c77482e45F1F44dE1745F52C74426C631bDD52" style="position:relative; top:8px">BNB (BNB)</a>
         address = cells[3].find('a')['href'].split('/')[2]
         name = cells[3].find('a').text.split(' ')[0]
         ticker = cells[3].find('a').text.split(' ')[1].lstrip('(').rstrip(')')
         # cells[4] - price USD:
         #        <td> <span style="margin-left:-4px">$6.1343</span><br/><font size="1">0.0015845654 Btc<br/>0.038537 Eth</font><br/><br/></td>
         price = float(cells[4].find('span').text.lstrip('$'))
         # cells[7] - market cap: <td>$802,357,584   </td>
         marketCap = int(cells[7].text.lstrip('$').rstrip().replace(',',''))
         
         results.append ({'address' : address, 'ticker' : ticker, 'marketCap' : marketCap, 'price' : price, 'name' : name}) 
      index += 1
   return results

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('outputFile')
   parser.add_argument('pages', type=int, help = 'number of pages to process at https://etherscan.io/tokens')
   args = parser.parse_args()
   main(args.outputFile, args.pages)
   