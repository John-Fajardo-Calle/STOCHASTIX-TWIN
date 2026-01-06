FROM node:20-bookworm-slim

WORKDIR /workspace/frontend

RUN apt-get update \
  && apt-get install -y --no-install-recommends git \
  && rm -rf /var/lib/apt/lists/*

RUN corepack enable

# Install deps (kept cached when possible)
COPY frontend/package.json /workspace/frontend/package.json
RUN npm install

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
