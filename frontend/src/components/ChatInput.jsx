import { useEffect, useRef, useState } from 'react'

const speechLanguageMap = {
  en: 'en-US',
  hi: 'hi-IN',
  es: 'es-ES',
  fr: 'fr-FR',
  de: 'de-DE',
  ar: 'ar-SA',
  'zh-CN': 'zh-CN',
  ja: 'ja-JP',
  mr: 'mr-IN',
  bn: 'bn-IN',
  ta: 'ta-IN',
  te: 'te-IN',
}

const speechErrorMessages = {
  'not-allowed': 'Microphone permission was denied. Allow microphone access and try again.',
  'service-not-allowed': 'Speech recognition service is blocked in this browser.',
  'no-speech': 'No speech was detected. Try speaking again closer to the microphone.',
  aborted: 'Voice input was stopped.',
  network: 'Speech recognition needs an internet connection in this browser.',
  'audio-capture': 'No microphone was found. Check your microphone device.',
}

export default function ChatInput({ disabled, language, onSendMessage }) {
  const [text, setText] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [speechError, setSpeechError] = useState('')
  const recognitionRef = useRef(null)
  const committedTranscriptRef = useRef('')

  useEffect(() => {
    return () => {
      recognitionRef.current?.stop()
    }
  }, [])

  const getSpeechRecognition = () => {
    return window.SpeechRecognition || window.webkitSpeechRecognition
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    recognitionRef.current?.stop()
    setIsListening(false)

    if (!text.trim()) {
      return
    }

    const message = text.trim()
    setText('')
    committedTranscriptRef.current = ''
    await onSendMessage(message)
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      event.currentTarget.form?.requestSubmit()
    }
  }

  const handleToggleListening = () => {
    const SpeechRecognition = getSpeechRecognition()
    if (!SpeechRecognition) {
      setSpeechError('Speech recognition is not supported in this browser. Please use Chrome or Microsoft Edge.')
      return
    }

    if (isListening) {
      recognitionRef.current?.stop()
      setIsListening(false)
      return
    }

    setSpeechError('')
    committedTranscriptRef.current = text.trim()

    const recognition = new SpeechRecognition()
    recognitionRef.current = recognition
    recognition.lang = speechLanguageMap[language] || 'en-US'
    recognition.continuous = true
    recognition.interimResults = true

    recognition.onresult = (event) => {
      let finalTranscript = ''
      let interimTranscript = ''

      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const transcript = event.results[index][0].transcript
        if (event.results[index].isFinal) {
          finalTranscript += transcript
        } else {
          interimTranscript += transcript
        }
      }

      if (finalTranscript.trim()) {
        committedTranscriptRef.current = [committedTranscriptRef.current, finalTranscript.trim()]
          .filter(Boolean)
          .join(' ')
      }

      setText([committedTranscriptRef.current, interimTranscript.trim()].filter(Boolean).join(' '))
    }

    recognition.onerror = (event) => {
      setSpeechError(speechErrorMessages[event.error] || `Speech recognition error: ${event.error}`)
      setIsListening(false)
    }

    recognition.onend = () => {
      setIsListening(false)
      committedTranscriptRef.current = ''
    }

    try {
      recognition.start()
      setIsListening(true)
    } catch (error) {
      setSpeechError('Voice input could not start. Please try again.')
      setIsListening(false)
    }
  }

  return (
    <div className="chat-input-wrap">
      {speechError ? <p className="speech-error">{speechError}</p> : null}
      <form className="chat-input-shell" onSubmit={handleSubmit}>
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Type symptoms or use the mic to speak..."
          disabled={disabled}
        />
        <button type="submit" className="primary-button" disabled={disabled || !text.trim()}>
          Send
        </button>
        <button
          type="button"
          className={`mic-button ${isListening ? 'listening' : ''}`}
          disabled={disabled}
          onClick={handleToggleListening}
          aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
          title={isListening ? 'Stop voice input' : 'Start voice input'}
        >
          <span aria-hidden="true">{isListening ? '■' : '🎤'}</span>
        </button>
      </form>
    </div>
  )
}
