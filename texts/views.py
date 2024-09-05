from django.shortcuts import render
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

def summarize(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        if not text:
            warning_message = "Please enter some text."
            context = {'warning_message': warning_message}
            return render(request, "texts/summarize.html", context)
        else:
            stopWords = set(stopwords.words("english"))
            words = word_tokenize(text)

            freqTable = dict()
            for word in words:
                word = word.lower()
                if word in stopWords:
                    continue
                if word in freqTable:
                    freqTable[word] += 1
                else:
                    freqTable[word] = 1

            sentences = sent_tokenize(text)
            sentenceValue = dict()

            for sentence in sentences:
                for word, freq in freqTable.items():
                    if word in sentence.lower():
                        if sentence in sentenceValue:
                            sentenceValue[sentence] += freq
                        else:
                            sentenceValue[sentence] = freq

            sumValues = 0
            for sentence in sentenceValue:
                sumValues += sentenceValue[sentence]

            average = int(sumValues / len(sentenceValue))

            summary_sentences = []
            for sentence in sentences:
                if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
                    summary_sentences.append(sentence)

            context = {'summary_sentences': summary_sentences}
            return render(request, "texts/summarize.html", context)
    else:
        return render(request, "texts/summarize.html")
