<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('comments', function (Blueprint $table) {
            // Xóa foreign key cũ
            $table->dropForeign(['parent_id']);

            // Thêm lại foreign key với ON DELETE CASCADE
            $table->foreign('parent_id')
                  ->references('comment_id')
                  ->on('comments')
                  ->onDelete('cascade');
        });
    }

    public function down(): void
    {
        Schema::table('comments', function (Blueprint $table) {
            // Xóa foreign key mới
            $table->dropForeign(['parent_id']);

            // Thêm lại foreign key cũ (không có CASCADE)
            $table->foreign('parent_id')
                  ->references('comment_id')
                  ->on('comments');
        });
    }
};
