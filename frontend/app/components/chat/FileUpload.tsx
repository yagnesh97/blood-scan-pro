"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { MessagePayload, ChatHistory, MessageType } from "./IFileUpload";
import React from "react";

const FileUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [userText, setUserText] = useState<string>("");
  const [chatHistory, setChatHistory] = useState<Array<ChatHistory>>(
    new Array()
  );
  const fileInputRef = useRef<HTMLInputElement>(null);

  //Public API that will echo messages sent to it back to the client
  const { sendMessage, lastMessage, readyState } = useWebSocket(
    "ws://localhost:8000/socket/ws"
  );

  useEffect(() => {
    if (lastMessage !== null) {
      const data = JSON.parse(lastMessage.data);
      setChatHistory((prev) => [
        ...prev,
        { message: data?.message, type: MessageType.SERVER },
      ]);
    }
  }, [lastMessage, setChatHistory]);

  const handleClickSendMessage = useCallback(
    (message: MessagePayload) => sendMessage(JSON.stringify(message)),
    []
  );
  const handleClickSendFile = useCallback(
    (file: ArrayBuffer) => sendMessage(file),
    []
  );

  const connectionStatus = {
    [ReadyState.CONNECTING]: "Connecting",
    [ReadyState.OPEN]: "Open",
    [ReadyState.CLOSING]: "Closing",
    [ReadyState.CLOSED]: "Closed",
    [ReadyState.UNINSTANTIATED]: "Uninstantiated",
  }[readyState];

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    setFile(droppedFile);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files && event.target.files[0];
    setFile(selectedFile);
  };

  const handleFormSubmit = (event: React.FormEvent) => {
    event.preventDefault();

    if (userText) {
      setChatHistory((prev) => [
        ...prev,
        { message: userText, type: MessageType.USER },
      ]);
    }

    // Send user text and file information to the server via WebSocket
    if (userText || file) {
      console.log(userText, file);
      const message = { text: userText, filename: file ? file.name : null };
      handleClickSendMessage(message);
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const fileData = e.target?.result;
          if (fileData instanceof ArrayBuffer) {
            handleClickSendFile(new Uint8Array(fileData));
          }
        };
        reader.readAsArrayBuffer(file);
      }
    }

    // Reset state
    setFile(null);
    setUserText("");
  };

  const handleClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-800 text-white">
      <div className="flex-1 container mx-auto p-6">
        <h1 className="text-3xl font-semibold mb-4">File Upload & Chat</h1>
        <div
          className="border-2 border-dashed border-gray-600 p-6 text-center cursor-pointer sm:flex sm:justify-center sm:items-center"
          onClick={handleClick}
          onDrop={handleDrop}
          onDragOver={(event) => event.preventDefault()}
        >
          <p className="mb-4 sm:mb-0">Click or drag and drop a file here</p>
          <input
            type="file"
            onChange={handleFileChange}
            ref={fileInputRef}
            className="hidden"
          />
        </div>
        {file && (
          <div className="mt-4">
            <h2 className="text-xl font-semibold">Selected File:</h2>
            <p>{file.name}</p>
          </div>
        )}
        <div className="mt-4">
          <h2 className="text-xl font-semibold mb-2">Chat History:</h2>
          <div>
            {chatHistory.map((entry, index) => (
              <div
                key={index}
                className={`mb-2 ${
                  entry.type === "user" ? "text-left" : "text-right"
                }`}
              >
                <div
                  className={`p-4 rounded-lg ${
                    entry.type === "user" ? "bg-gray-600" : "bg-blue-500"
                  }`}
                >
                  {entry.message}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <form
        onSubmit={handleFormSubmit}
        className="p-4 bg-gray-700 sticky bottom-0"
      >
        <div className="flex items-center">
          <textarea
            value={userText}
            onChange={(e) => setUserText(e.target.value)}
            placeholder="Enter your message..."
            className="flex-1 p-2 border border-gray-600 rounded-l resize-none text-black"
            rows={3}
          />
          <button
            type="submit"
            disabled={!userText && !file}
            className={`bg-blue-500 text-white py-2 px-4 rounded-r ${
              !userText && !file && "opacity-50 cursor-not-allowed"
            }`}
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default FileUpload;
