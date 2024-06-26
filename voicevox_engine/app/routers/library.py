"""音声ライブラリ機能を提供する API Router"""

import asyncio
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request

from voicevox_engine.engine_manifest import EngineManifest
from voicevox_engine.library_manager import LibraryManager
from voicevox_engine.model import DownloadableLibraryInfo, InstalledLibraryInfo

from ..dependencies import check_disabled_mutable_api


def generate_library_router(
    engine_manifest_data: EngineManifest, library_manager: LibraryManager
) -> APIRouter:
    """音声ライブラリ API Router を生成する"""
    router = APIRouter(tags=["音声ライブラリ管理"])

    @router.get(
        "/downloadable_libraries",
        response_description="ダウンロード可能な音声ライブラリの情報リスト",
    )
    def downloadable_libraries() -> list[DownloadableLibraryInfo]:
        """
        ダウンロード可能な音声ライブラリの情報を返します。
        """
        if not engine_manifest_data.supported_features.manage_library:
            raise HTTPException(status_code=404, detail="この機能は実装されていません")
        return library_manager.downloadable_libraries()

    @router.get(
        "/installed_libraries",
        response_description="インストールした音声ライブラリの情報",
    )
    def installed_libraries() -> dict[str, InstalledLibraryInfo]:
        """
        インストールした音声ライブラリの情報を返します。
        """
        if not engine_manifest_data.supported_features.manage_library:
            raise HTTPException(status_code=404, detail="この機能は実装されていません")
        return library_manager.installed_libraries()

    @router.post(
        "/install_library/{library_uuid}",
        status_code=204,
        dependencies=[Depends(check_disabled_mutable_api)],
    )
    async def install_library(
        library_uuid: Annotated[str, Path(description="音声ライブラリのID")],
        request: Request,
    ) -> None:
        """
        音声ライブラリをインストールします。
        音声ライブラリのZIPファイルをリクエストボディとして送信してください。
        """
        if not engine_manifest_data.supported_features.manage_library:
            raise HTTPException(status_code=404, detail="この機能は実装されていません")
        archive = BytesIO(await request.body())
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, library_manager.install_library, library_uuid, archive
        )

    @router.post(
        "/uninstall_library/{library_uuid}",
        status_code=204,
        dependencies=[Depends(check_disabled_mutable_api)],
    )
    def uninstall_library(
        library_uuid: Annotated[str, Path(description="音声ライブラリのID")]
    ) -> None:
        """
        音声ライブラリをアンインストールします。
        """
        if not engine_manifest_data.supported_features.manage_library:
            raise HTTPException(status_code=404, detail="この機能は実装されていません")
        library_manager.uninstall_library(library_uuid)

    return router
