#!/usr/bin/env python3
"""
auto_runner.py — Motor CLI de Generación y Auditoría Automática (Integración con Claude)
Permite que Claude (o cualquier cron/webhook) genere campañas, edite agentes y audite
la regla 85% Imagen / 15% Texto + Logo pequeño en esquina inferior derecha.
"""
import argparse
import json
import os
from datetime import datetime, timedelta

from server import CLIENTS_DB_PATH, POSTS_DB_PATH, SECRETS_PATH, load_json, save_json, synthesize_multi_agent_post


def sync_bundle(db, posts):
    bundle_path = os.path.join(os.path.dirname(CLIENTS_DB_PATH), "..", "public", "data_bundle.js")
    bundle = {
        "meta_portfolio": db.get("meta_portfolio", {}),
        "ai_engines": db.get("ai_engines", []),
        "clients": db.get("clients", []),
        "posts": posts,
        "configured_keys": {}
    }
    with open(os.path.abspath(bundle_path), "w", encoding="utf-8") as f:
        f.write("window.__INITIAL_HUB_STATE__ = " + json.dumps(bundle, ensure_ascii=False) + ";\n")


def main():
    parser = argparse.ArgumentParser(description="DALE+ AI Hub — CLI de Automatización para Claude")
    parser.add_argument("--client", type=str, help="Nombre o Asset ID del cliente")
    parser.add_argument("--topic", type=str, default="", help="Tema o promoción específica")
    parser.add_argument("--days", type=int, default=1, help="Número de días/posts a generar")
    parser.add_argument("--ai", type=str, default="council", help="IA líder (claude, chatgpt, kimi, manus, gemini, council)")
    parser.add_argument("--audit-85-15", action="store_true", help="Audita que toda la cola cumpla 85% imagen / 15% texto y logo inf. derecha")
    args = parser.parse_args()

    db = load_json(CLIENTS_DB_PATH, {})
    posts = load_json(POSTS_DB_PATH, [])
    secrets = load_json(SECRETS_PATH, {})

    if args.audit_85_15:
        print(f"🔍 Auditando {len(posts)} publicaciones bajo la regla 85% Imagen / 15% Texto + Logo Inf. Derecha...")
        fixed = 0
        for p in posts:
            if p.get("logo_pos") != "bottom-right-small":
                p["logo_pos"] = "bottom-right-small"
                fixed += 1
            raw_tokens = " ".join([p.get("headline_15", ""), p.get("sub_15", ""), p.get("offer_15", "")]).split()
            words = len([w for w in raw_tokens if w not in ("|", "x", "•", ">", "-") and any(c.isalnum() for c in w)])
            status_icon = "✅" if words <= 10 else "⚠️"
            print(f"  {status_icon} [{p['client_name'][:28]:28s}] Palabras en arte: {words:2d} | Logo: {p['logo_pos']}")
        if fixed:
            save_json(POSTS_DB_PATH, posts)
            sync_bundle(db, posts)
        print("✔ Auditoría completada.")
        return

    if args.client:
        q = args.client.lower()
        target = next(
            (c for c in db.get("clients", []) if q in c["name"].lower() or q == c["asset_id"] or q == c["id"]),
            None
        )
        if not target:
            print(f"❌ No se encontró un cliente que coincida con: {args.client}")
            return

        pillars = target["agent"].get("content_pillars", ["Contenido de Valor"])
        created = []
        now = datetime.now()
        for d in range(args.days):
            topic = args.topic if (args.topic and args.days == 1) else f"{pillars[d % len(pillars)]} — {target['name']}"
            post = synthesize_multi_agent_post(target, topic, "Arte 85/15 + Copy", args.ai, secrets)
            post["id"] = f"post_auto_{int(now.timestamp()*1000)}_{d}"
            post["scheduled_for"] = (now + timedelta(days=d + 1)).strftime("%Y-%m-%d 13:00")
            post["logo_pos"] = "bottom-right-small"
            posts.insert(0, post)
            created.append(post)
            print(f"✅ Generado Día {d+1}: {target['name']} -> {topic}")

        save_json(POSTS_DB_PATH, posts)
        sync_bundle(db, posts)
        print(f"🚀 Se agregaron {len(created)} publicaciones a data/posts_queue.json")


if __name__ == "__main__":
    main()
