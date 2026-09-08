#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import secrets
from pathlib import Path

EXPECTED_INDEX_BYTES = 42325
EXPECTED_INDEX_SHA256 = "9ffd152f68e1b377ef72377fcbc340f40759e3ee9945035fec87a2332addc045"
EXPECTED_VIDEO_BYTES = 1034533
EXPECTED_VIDEO_SHA256 = "1207773ab6194f8b29ed03e08d184dce7dfe3140ebbc8235dedf00e9c8067fc7"
LEGACY_VIDEO = "/join-us/video-header.mp4?v=6"
SIGNATURE = "TAM_JOIN_US_WORDPRESS_FORCE_V1"
BEGIN = "// BEGIN TAMIYOUZ JOIN US FORCE TEMPLATE V1"
END = "// END TAMIYOUZ JOIN US FORCE TEMPLATE V1"

CAREERS_BLOCK_RE = re.compile(r"(?ms)^# BEGIN Careers Page\s*\r?\n.*?^# END Careers Page\s*(?:\r?\n)?")
CAREERS_RULE_RE = re.compile(r"(?m)^\s*RewriteRule\s+\^join-us/\?\$\s+/join-us/index\.html\s+\[L\]\s*$")
WP_FRONT_RE = re.compile(r"(?m)^\s*RewriteRule\s+\.\s+index\.php\s+\[L\]\s*$")

DENY_HTACCESS = """Options -Indexes
<IfModule mod_authz_core.c>
    Require all denied
</IfModule>
<IfModule !mod_authz_core.c>
    Order Allow,Deny
    Deny from all
</IfModule>
"""

FORCE_BLOCK = r'''
// BEGIN TAMIYOUZ JOIN US FORCE TEMPLATE V1
if (!function_exists('tamiyouz_join_us_force_template_v1')) {
    function tamiyouz_join_us_force_template_v1($template) {
        if (!is_admin() && is_page('join-us')) {
            $join_us_template = get_stylesheet_directory() . '/page-join-us.php';
            if (is_file($join_us_template)) {
                return $join_us_template;
            }
        }
        return $template;
    }
    add_filter('template_include', 'tamiyouz_join_us_force_template_v1', PHP_INT_MAX);
}
// END TAMIYOUZ JOIN US FORCE TEMPLATE V1
'''


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def php_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main():
    ap = argparse.ArgumentParser(description="Build final Join Us WordPress migration with forced template_include override.")
    ap.add_argument("--index", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--htaccess", required=True)
    ap.add_argument("--functions", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--token", default=None)
    args = ap.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    index_raw = Path(args.index).read_bytes()
    video_raw = Path(args.video).read_bytes()
    ht_raw = Path(args.htaccess).read_bytes()
    functions_raw = Path(args.functions).read_bytes()

    if len(index_raw) != EXPECTED_INDEX_BYTES or sha256_bytes(index_raw) != EXPECTED_INDEX_SHA256:
        raise SystemExit("index.html trusted baseline mismatch")
    if len(video_raw) != EXPECTED_VIDEO_BYTES or sha256_bytes(video_raw) != EXPECTED_VIDEO_SHA256:
        raise SystemExit("video-header.mp4 trusted baseline mismatch")

    html = index_raw.decode("utf-8")
    required = [
        "https://careers.tamiyouzplaform.com/",
        "https://careers.tamiyouzplaform.com/api/v1/rakan/chat",
        "fetch('/join-us/notify.php'",
        "e.data.type === 'formSubmission'",
        LEGACY_VIDEO,
    ]
    for marker in required:
        if marker not in html:
            raise SystemExit(f"missing Join Us marker: {marker}")
    if html.count(LEGACY_VIDEO) != 1:
        raise SystemExit("expected exactly one legacy video URL")

    ht = ht_raw.decode("utf-8")
    blocks = CAREERS_BLOCK_RE.findall(ht)
    if len(blocks) != 1 or not CAREERS_RULE_RE.search(blocks[0]):
        raise SystemExit("expected exactly one legacy Careers Page block with join-us rewrite")
    if not WP_FRONT_RE.search(ht):
        raise SystemExit("WordPress front-controller rule missing")
    ht_after = CAREERS_BLOCK_RE.sub("", ht, count=1)
    if CAREERS_RULE_RE.search(ht_after) or not WP_FRONT_RE.search(ht_after):
        raise SystemExit("unsafe .htaccess transform")

    functions = functions_raw.decode("utf-8")
    if functions.count(BEGIN) or functions.count(END) or "tamiyouz_join_us_force_template_v1" in functions:
        raise SystemExit("force-template block already present; refusing duplicate")
    functions_after = functions.rstrip() + "\n\n" + FORCE_BLOCK.lstrip()
    if functions_after.count(BEGIN) != 1 or functions_after.count(END) != 1:
        raise SystemExit("force-template block count invalid")

    wp_video = "<?php echo esc_url(get_stylesheet_directory_uri() . '/assets/join-us/video-header.mp4?v=6'); ?>"
    transformed = html.replace(LEGACY_VIDEO, wp_video, 1)
    page = ("<?php\ndefined('ABSPATH') || exit;\n?>\n<!-- " + SIGNATURE + " -->\n" + transformed).encode("utf-8")

    (out / "page-join-us.php").write_bytes(page)
    (out / "functions.php.after").write_text(functions_after, encoding="utf-8")
    (out / ".htaccess.after").write_text(ht_after, encoding="utf-8")
    (out / "backup-deny.htaccess").write_text(DENY_HTACCESS, encoding="utf-8")

    token = args.token or secrets.token_urlsafe(48)
    nonce = secrets.token_hex(8)
    helper_name = f"join-us-force-bootstrap-v8-{nonce}.php"
    state_key = f"_tamiyouz_join_us_force_v8_{nonce}"

    helper = f'''<?php
header('Content-Type: application/json; charset=utf-8');
$expectedToken = {php_string(token)};
$provided = isset($_GET['token']) ? (string) $_GET['token'] : '';
if ($provided === '' || !hash_equals($expectedToken, $provided)) {{
    http_response_code(403);
    echo json_encode(['success'=>false,'error'=>'forbidden']);
    exit;
}}
require_once __DIR__ . '/wp-load.php';
$stateKey = {php_string(state_key)};
$action = isset($_GET['action']) ? (string) $_GET['action'] : 'inspect';
function ju8_out($p,$s=200) {{ http_response_code($s); echo wp_json_encode($p, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE); exit; }}
function ju8_page() {{
    $posts = get_posts(['name'=>'join-us','post_type'=>'page','post_status'=>['publish','future','draft','pending','private','trash'],'numberposts'=>10,'suppress_filters'=>true]);
    if (count($posts) !== 1) ju8_out(['success'=>false,'error'=>'join_us_page_count','count'=>count($posts),'ids'=>array_map(fn($p)=>(int)$p->ID,$posts)],409);
    return $posts[0];
}}
function ju8_snap($p) {{
    return ['ID'=>(int)$p->ID,'status'=>(string)$p->post_status,'slug'=>(string)$p->post_name,'title'=>(string)$p->post_title,'template_meta'=>(string)get_post_meta($p->ID,'_wp_page_template',true)];
}}
function ju8_purge($id) {{
    $done=[];
    if (has_action('litespeed_purge_url') !== false) {{ do_action('litespeed_purge_url', home_url('/join-us/')); $done[]='litespeed_purge_url'; }}
    if (has_action('litespeed_purge_post') !== false) {{ do_action('litespeed_purge_post',(int)$id); $done[]='litespeed_purge_post'; }}
    if (has_action('litespeed_purge_all') !== false) {{ do_action('litespeed_purge_all','Join Us forced template cutover V8'); $done[]='litespeed_purge_all'; }}
    return $done;
}}
if ($action === 'inspect') {{
    $p = ju8_page();
    ju8_out(['success'=>true,'page'=>ju8_snap($p),'url_to_postid'=>(int)url_to_postid(home_url('/join-us/')),'stylesheet'=>(string)get_option('stylesheet'),'located'=>locate_template(['page-join-us.php'],false,false),'state_exists'=>(get_option($stateKey,null)!==null)]);
}}
if ($action === 'prepare') {{
    if (get_option($stateKey,null)!==null) ju8_out(['success'=>false,'error'=>'state_exists'],409);
    $p=ju8_page();
    $state=['before'=>ju8_snap($p)];
    if (!add_option($stateKey,$state,'',false)) ju8_out(['success'=>false,'error'=>'state_save_failed'],500);
    if ($p->post_status === 'trash' && !wp_untrash_post($p->ID)) ju8_out(['success'=>false,'error'=>'untrash_failed'],500);
    $r=wp_update_post(['ID'=>$p->ID,'post_name'=>'join-us','post_status'=>'draft'],true);
    if (is_wp_error($r)) ju8_out(['success'=>false,'error'=>'prepare_failed','message'=>$r->get_error_message()],500);
    delete_post_meta($p->ID,'_wp_page_template');
    clean_post_cache($p->ID);
    ju8_out(['success'=>true,'page'=>ju8_snap(get_post($p->ID))]);
}}
if ($action === 'activate') {{
    $state=get_option($stateKey,null); if (!is_array($state)) ju8_out(['success'=>false,'error'=>'missing_state'],409);
    $id=(int)($state['before']['ID']??0); $p=get_post($id); if(!$p) ju8_out(['success'=>false,'error'=>'missing_page'],409);
    $r=wp_update_post(['ID'=>$id,'post_name'=>'join-us','post_status'=>'publish'],true);
    if(is_wp_error($r)) ju8_out(['success'=>false,'error'=>'activate_failed','message'=>$r->get_error_message()],500);
    delete_post_meta($id,'_wp_page_template');
    flush_rewrite_rules(false); clean_post_cache($id);
    $purged=ju8_purge($id);
    ju8_out(['success'=>true,'page'=>ju8_snap(get_post($id)),'url_to_postid'=>(int)url_to_postid(home_url('/join-us/')),'purged'=>$purged]);
}}
if ($action === 'rollback') {{
    $state=get_option($stateKey,null);
    if (!is_array($state)) ju8_out(['success'=>true,'message'=>'no_state']);
    $b=$state['before']; $id=(int)$b['ID'];
    if (($b['status']??'') === 'trash') {{ wp_trash_post($id); }} else {{
        $r=wp_update_post(['ID'=>$id,'post_status'=>$b['status'],'post_name'=>$b['slug'],'post_title'=>$b['title']],true);
        if(is_wp_error($r)) ju8_out(['success'=>false,'error'=>'rollback_post_failed','message'=>$r->get_error_message()],500);
    }}
    if (($b['template_meta']??'') !== '') update_post_meta($id,'_wp_page_template',$b['template_meta']); else delete_post_meta($id,'_wp_page_template');
    delete_option($stateKey); flush_rewrite_rules(false); ju8_purge($id);
    ju8_out(['success'=>true]);
}}
if ($action === 'cleanup') {{ delete_option($stateKey); ju8_out(['success'=>true]); }}
ju8_out(['success'=>false,'error'=>'unknown_action'],400);
'''
    (out / helper_name).write_text(helper, encoding="utf-8")

    manifest = {
        "builder": "BUILD-JOIN-US-WORDPRESS-FORCE-TEMPLATE-V8.py",
        "source_index_bytes": len(index_raw),
        "source_index_sha256": sha256_bytes(index_raw),
        "source_video_bytes": len(video_raw),
        "source_video_sha256": sha256_bytes(video_raw),
        "functions_before_sha256": sha256_bytes(functions_raw),
        "functions_after_sha256": sha256_bytes(functions_after.encode('utf-8')),
        "htaccess_before_sha256": sha256_bytes(ht_raw),
        "htaccess_after_sha256": sha256_bytes(ht_after.encode('utf-8')),
        "page_file_sha256": sha256_bytes(page),
        "page_file_bytes": len(page),
        "page_signature": SIGNATURE,
        "force_block_begin": BEGIN,
        "force_block_end": END,
        "helper_filename": helper_name,
        "helper_sha256": sha256_bytes(helper.encode('utf-8')),
        "state_key": state_key,
        "one_time_token": token,
        "strategy": "FORCE_TEMPLATE_INCLUDE_AT_PHP_INT_MAX_FOR_JOIN_US_ONLY",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    redacted=dict(manifest); redacted['one_time_token']='REDACTED'; print(json.dumps(redacted,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
